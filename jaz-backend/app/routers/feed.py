from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LearningPost, Child, LearningActivity
from app.schemas import LearningPostCreate, LearningPostResponse
from app.gamification import calculate_child_level, calculate_rating

router = APIRouter()


@router.post("/", response_model=LearningPostResponse)
def create_learning_post(data: LearningPostCreate, db: Session = Depends(get_db)):
    post = LearningPost(
        title=data.title,
        content=data.content,
        category=data.category,
        age_min=data.age_min,
        age_max=data.age_max,
        stars_reward=data.stars_reward
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


@router.get("/{child_id}")
def get_learning_feed(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    posts = db.query(LearningPost).filter(
        LearningPost.age_min <= child.age,
        LearningPost.age_max >= child.age
    ).order_by(LearningPost.created_at.desc()).all()

    return {
        "child_id": child.id,
        "child_name": child.name,
        "feed": posts
    }


@router.post("/{child_id}/complete/{post_id}")
def complete_learning_post(
    child_id: int,
    post_id: int,
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == child_id).first()
    post = db.query(LearningPost).filter(LearningPost.id == post_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if not post:
        raise HTTPException(status_code=404, detail="Learning post not found")

    child.wisdom_stars += post.stars_reward
    child.level = calculate_child_level(child.wisdom_stars)
    child.rating = calculate_rating(child.wisdom_stars)

    activity = LearningActivity(
        child_id=child.id,
        topic=post.category,
        activity_type="learning_post",
        summary=f"Completed learning post: {post.title}",
        stars_earned=post.stars_reward
    )

    db.add(activity)
    db.commit()

    return {
        "message": "Learning completed",
        "child": child.name,
        "post": post.title,
        "stars_earned": post.stars_reward,
        "total_wisdom_stars": child.wisdom_stars,
        "level": child.level,
        "rating": child.rating
    }
