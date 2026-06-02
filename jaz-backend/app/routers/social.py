from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from app.database import get_db
from app.models import Child, SocialPost, PostBadge, LearningActivity
from app.schemas import SocialPostCreate, SocialPostResponse, BadgeCreate
from app.gamification import calculate_child_level, calculate_rating

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SAFE_BADGES = [
    "Wisdom Star",
    "Kind Work",
    "Creative Mind",
    "Great Idea",
    "Good Learner"
]


def moderate_child_post(title: str, content: str):
    prompt = f"""
    You are a child safety moderation assistant for JAZ.

    Review this child post.

    Title: {title}
    Content: {content}

    Return only one word:
    SAFE or UNSAFE

    Mark UNSAFE if it includes:
    adult content, sexual content, violence, bullying, self-harm,
    private personal information, stranger contact, hate, abuse,
    dangerous behaviour, or anything unsuitable for children.
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a strict child safety moderator."},
            {"role": "user", "content": prompt}
        ]
    )

    result = completion.choices[0].message.content.strip().upper()

    return result == "SAFE"


@router.post("/", response_model=SocialPostResponse)
def create_social_post(data: SocialPostCreate, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    is_safe = moderate_child_post(data.title, data.content)

    post = SocialPost(
        child_id=data.child_id,
        title=data.title,
        content=data.content,
        media_url=data.media_url,
        category=data.category,
        status="approved" if is_safe else "blocked"
    )

    db.add(post)

    if is_safe:
        activity = LearningActivity(
            child_id=child.id,
            topic="Creative Sharing",
            activity_type="social_post",
            summary=f"Created post: {data.title}",
            stars_earned=2
        )

        child.wisdom_stars += 2
        child.level = calculate_child_level(child.wisdom_stars)
        child.rating = calculate_rating(child.wisdom_stars)
        db.add(activity)

    db.commit()
    db.refresh(post)

    return post


@router.get("/feed/{child_id}")
def get_safe_social_feed(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    posts = db.query(SocialPost).filter(
        SocialPost.status == "approved"
    ).order_by(SocialPost.created_at.desc()).all()

    return {
        "child_id": child.id,
        "child_name": child.name,
        "safe_social_feed": posts
    }


@router.post("/{post_id}/badge")
def give_badge(post_id: int, data: BadgeCreate, db: Session = Depends(get_db)):
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if data.badge not in SAFE_BADGES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid badge. Use one of: {SAFE_BADGES}"
        )

    badge = PostBadge(
        post_id=post.id,
        badge=data.badge
    )

    post.stars_received += 1

    child = db.query(Child).filter(Child.id == post.child_id).first()
    if child:
        child.wisdom_stars += 1
        child.level = calculate_child_level(child.wisdom_stars)
        child.rating = calculate_rating(child.wisdom_stars)

    db.add(badge)
    db.commit()

    return {
        "message": "Badge added",
        "post_id": post.id,
        "badge": data.badge,
        "stars_received": post.stars_received
    }


@router.get("/{post_id}/badges")
def get_post_badges(post_id: int, db: Session = Depends(get_db)):
    badges = db.query(PostBadge).filter(PostBadge.post_id == post_id).all()

    return {
        "post_id": post_id,
        "badges": badges
    }
