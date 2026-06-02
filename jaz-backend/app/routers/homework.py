from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from app.database import get_db
from app.models import Child, HomeworkSession, LearningActivity
from app.schemas import HomeworkHelpRequest
from app.gamification import calculate_child_level, calculate_rating

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.post("/help")
def help_with_homework(data: HomeworkHelpRequest, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    system_prompt = f"""
    You are JAZ Homework Helper, a safe educational tutor for children.

    Child:
    Name: {child.name}
    Age: {child.age}
    Interests: {child.interests}

    Subject:
    {data.subject}

    Rules:
    - Do not just give the final answer immediately.
    - Explain step by step.
    - Ask guiding questions.
    - Encourage the child to think.
    - Use age-appropriate language.
    - Keep the explanation safe, simple, and positive.
    - Never discuss adult, unsafe, harmful, or inappropriate content.
    - If the question is unsafe, redirect to a safe learning topic.
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": data.question}
        ]
    )

    ai_explanation = completion.choices[0].message.content
    stars = 3

    session = HomeworkSession(
        child_id=child.id,
        subject=data.subject,
        question=data.question,
        ai_explanation=ai_explanation,
        learning_points=f"Subject: {data.subject}",
        stars_earned=stars
    )

    child.wisdom_stars += stars
    child.level = calculate_child_level(child.wisdom_stars)
    child.rating = calculate_rating(child.wisdom_stars)

    activity = LearningActivity(
        child_id=child.id,
        topic=data.subject,
        activity_type="homework_help",
        summary=f"Homework help requested: {data.question[:80]}",
        stars_earned=stars
    )

    db.add(session)
    db.add(activity)
    db.commit()
    db.refresh(session)

    return {
        "message": "Homework help completed",
        "subject": data.subject,
        "question": data.question,
        "explanation": ai_explanation,
        "stars_earned": stars,
        "total_wisdom_stars": child.wisdom_stars,
        "level": child.level,
        "rating": child.rating
    }


@router.get("/sessions/{child_id}")
def get_homework_sessions(child_id: int, db: Session = Depends(get_db)):
    sessions = db.query(HomeworkSession).filter(
        HomeworkSession.child_id == child_id
    ).order_by(HomeworkSession.created_at.desc()).all()

    return {
        "child_id": child_id,
        "homework_sessions": sessions
    }