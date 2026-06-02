from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from app.database import get_db
from app.models import Child, Community, CommunityMember, CommunityPost
from app.schemas import CommunityCreate, CommunityJoinRequest, CommunityPostCreate

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def moderate_community_message(content: str):
    prompt = f"""
    You are a strict child-safety moderator for JAZ.

    Review this community message:

    {content}

    Return only one word:
    SAFE or UNSAFE

    Mark UNSAFE if the content includes:
    adult content, sexual content, violence, bullying, insults, self-harm,
    hate, dangerous behaviour, personal contact details, stranger meeting,
    private information, manipulation, or anything unsuitable for children.
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You moderate child community content."},
            {"role": "user", "content": prompt}
        ]
    )

    result = completion.choices[0].message.content.strip().upper()
    return result == "SAFE"


@router.post("/")
def create_community(data: CommunityCreate, db: Session = Depends(get_db)):
    community = Community(
        name=data.name,
        description=data.description,
        category=data.category,
        age_min=data.age_min,
        age_max=data.age_max
    )

    db.add(community)
    db.commit()
    db.refresh(community)

    return community


@router.get("/")
def list_communities(db: Session = Depends(get_db)):
    return db.query(Community).all()


@router.post("/{community_id}/join")
def join_community(
    community_id: int,
    data: CommunityJoinRequest,
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == data.child_id).first()
    community = db.query(Community).filter(Community.id == community_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    if child.age < community.age_min or child.age > community.age_max:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Child age {child.age} is not suitable for this community. "
                f"Required age range: {community.age_min}-{community.age_max}."
            )
        )

    existing = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.child_id == child.id
    ).first()

    if existing:
        return {"message": "Child already joined this community"}

    member = CommunityMember(
        community_id=community_id,
        child_id=child.id
    )

    db.add(member)
    db.commit()

    return {
        "message": "Child joined community successfully",
        "community": community.name,
        "child": child.name
    }


@router.post("/{community_id}/posts")
def create_community_post(
    community_id: int,
    data: CommunityPostCreate,
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == data.child_id).first()
    community = db.query(Community).filter(Community.id == community_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    membership = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.child_id == child.id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="Child must join community before posting")

    is_safe = moderate_community_message(data.content)

    post = CommunityPost(
        community_id=community_id,
        child_id=child.id,
        content=data.content,
        status="approved" if is_safe else "blocked"
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


@router.get("/{community_id}/posts")
def get_community_posts(community_id: int, db: Session = Depends(get_db)):
    posts = db.query(CommunityPost).filter(
        CommunityPost.community_id == community_id,
        CommunityPost.status == "approved"
    ).order_by(CommunityPost.created_at.desc()).all()

    return {
        "community_id": community_id,
        "posts": posts
    }
