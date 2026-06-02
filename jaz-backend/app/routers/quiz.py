from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from app.database import get_db
from app.models import Child, QuizSession, LearningActivity
from app.schemas import QuizGenerateRequest, QuizSubmitRequest
from app.gamification import calculate_child_level, calculate_rating

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.post("/generate")
def generate_quiz(data: QuizGenerateRequest, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    system_prompt = f"""
    You are JAZ Quiz Builder, a safe educational quiz generator for children.

    Child:
    Name: {child.name}
    Age: {child.age}
    Interests: {child.interests}

    Rules:
    - Create age-appropriate questions.
    - Keep it friendly and encouraging.
    - Avoid unsafe, adult, violent, or inappropriate content.
    - Return quiz in clear JSON-like format.
    - Include answer options and correct answers.
    """

    user_prompt = f"""
    Generate {data.number_of_questions} {data.difficulty} quiz questions about {data.topic}.

    Format:
    [
      {{
        "question": "...",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "..."
      }}
    ]
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.5,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    questions = completion.choices[0].message.content

    quiz = QuizSession(
        child_id=child.id,
        topic=data.topic,
        difficulty=data.difficulty,
        questions=questions
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return {
        "message": "Quiz generated",
        "quiz_id": quiz.id,
        "topic": data.topic,
        "difficulty": data.difficulty,
        "questions": questions
    }


@router.post("/submit")
def submit_quiz(data: QuizSubmitRequest, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == data.child_id).first()
    quiz = db.query(QuizSession).filter(QuizSession.id == data.quiz_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.child_id != child.id:
        raise HTTPException(status_code=403, detail="Quiz does not belong to this child")

    stars = max(1, data.score)

    quiz.score = data.score
    quiz.stars_earned = stars

    child.wisdom_stars += stars
    child.level = calculate_child_level(child.wisdom_stars)
    child.rating = calculate_rating(child.wisdom_stars)

    activity = LearningActivity(
        child_id=child.id,
        topic=quiz.topic,
        activity_type="quiz",
        summary=f"Completed quiz on {quiz.topic} with score {data.score}",
        stars_earned=stars
    )

    db.add(activity)
    db.commit()

    return {
        "message": "Quiz submitted",
        "score": data.score,
        "stars_earned": stars,
        "total_wisdom_stars": child.wisdom_stars,
        "level": child.level,
        "rating": child.rating
    }


@router.get("/sessions/{child_id}")
def get_quiz_sessions(child_id: int, db: Session = Depends(get_db)):
    quizzes = db.query(QuizSession).filter(
        QuizSession.child_id == child_id
    ).order_by(QuizSession.created_at.desc()).all()

    return {
        "child_id": child_id,
        "quiz_sessions": quizzes
    }