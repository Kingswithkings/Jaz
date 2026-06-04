from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from app.database import get_db
from app.models import Child, LearningActivity, LearningGoal, LearningPath
from app.schemas import LearningPathGenerateRequest

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.post("/generate")
def generate_learning_path(
    data: LearningPathGenerateRequest,
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    goals = db.query(LearningGoal).filter(
        LearningGoal.child_id == child.id
    ).all()

    activities = db.query(LearningActivity).filter(
        LearningActivity.child_id == child.id
    ).order_by(LearningActivity.created_at.desc()).limit(10).all()

    goals_text = "\n".join(
        [f"- {goal.title}: {goal.description or ''}" for goal in goals]
    ) or "No goals yet."

    activities_text = "\n".join(
        [f"- {activity.topic}: {activity.summary}" for activity in activities]
    ) or "No previous activities yet."

    focus_area = data.focus_area or "general learning growth"

    system_prompt = f"""
    You are JAZ Learning Path Builder, a safe educational planner for children.

    Child profile:
    Name: {child.name}
    Age: {child.age}
    Interests: {child.interests}
    Level: {child.level}
    Wisdom Stars: {child.wisdom_stars}

    Current learning goals:
    {goals_text}

    Recent learning activities:
    {activities_text}

    Focus area:
    {focus_area}

    Create a 7-day personalized learning path.

    Rules:
    - Make it age-appropriate.
    - Make it encouraging and simple.
    - Include daily learning tasks.
    - Include creative tasks.
    - Include quiz or reflection tasks.
    - Keep it child-safe.
    - Do not include unsafe websites or adult content.
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.5,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate the personalized 7-day learning path."}
        ]
    )

    path_content = completion.choices[0].message.content

    learning_path = LearningPath(
        child_id=child.id,
        title=f"{child.name}'s 7-Day Learning Path",
        description=f"Personalized learning path focused on {focus_area}",
        path_content=path_content,
        status="active"
    )

    db.add(learning_path)
    db.commit()
    db.refresh(learning_path)

    return {
        "message": "Learning path generated",
        "learning_path": learning_path
    }


@router.get("/{child_id}")
def get_learning_paths(child_id: int, db: Session = Depends(get_db)):
    paths = db.query(LearningPath).filter(
        LearningPath.child_id == child_id
    ).order_by(LearningPath.created_at.desc()).all()

    return {
        "child_id": child_id,
        "learning_paths": paths
    }