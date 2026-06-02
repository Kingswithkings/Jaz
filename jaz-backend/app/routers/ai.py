from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from app.database import get_db
from app.models import Child, LearningActivity, AIChatLog
from app.schemas import AIChatRequest, AIChatResponse
from app.vector_store import save_child_memory, search_child_memory
from app.gamification import calculate_child_level, calculate_rating

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.post("/chat", response_model=AIChatResponse)
def chat_with_jaz(data: AIChatRequest, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    try:
        memories = search_child_memory(
            child_id=child.id,
            query=data.message,
            top_k=3
        )
    except RuntimeError:
        memories = []

    memory_context = "\n".join(
        [f"- {memory['text']}" for memory in memories]
    )

    system_prompt = f"""
    You are JAZ, a safe, kind, educational AI companion for children.

    Child:
    Name: {child.name}
    Age: {child.age}
    Interests: {child.interests}
    Level: {child.level}
    Wisdom Stars: {child.wisdom_stars}

    Relevant learning memory:
    {memory_context}

    Safety rules:
    - Be warm, simple, and conversational.
    - Encourage learning, creativity, kindness, and wisdom.
    - Do not discuss adult, sexual, violent, harmful, or unsafe content.
    - Do not ask for private information.
    - Do not encourage children to meet strangers.
    - If unsafe content appears, gently redirect to learning.
    - Keep responses short and age-appropriate.
    - Ask one positive follow-up question.
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.5,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": data.message}
        ]
    )

    response = completion.choices[0].message.content

    child.wisdom_stars += 1
    child.level = calculate_child_level(child.wisdom_stars)
    child.rating = calculate_rating(child.wisdom_stars)

    activity = LearningActivity(
        child_id=child.id,
        topic="AI Conversation",
        activity_type="chat",
        summary=data.message,
        stars_earned=1
    )

    chat_log = AIChatLog(
        child_id=child.id,
        message=data.message,
        response=response
    )

    try:
        save_child_memory(
            child_id=child.id,
            text=f"{child.name} asked: {data.message}. JAZ replied: {response}",
            memory_type="ai_chat",
            metadata={
                "topic": "AI Conversation",
                "stars_earned": 1
            }
        )
    except RuntimeError:
        pass

    db.add(activity)
    db.add(chat_log)
    db.commit()

    return {"response": response}
