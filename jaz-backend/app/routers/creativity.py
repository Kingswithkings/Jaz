from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from app.database import get_db
from app.models import Child, CreativeProject, LearningActivity
from app.schemas import CreativeProjectCreate, CreativeAIRequest
from app.gamification import calculate_child_level, calculate_rating

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


ALLOWED_PROJECT_TYPES = [
    "story",
    "poem",
    "drawing",
    "comic",
    "music",
    "bible_reflection",
    "school_project"
]


def generate_creative_response(child: Child, project_type: str, prompt: str):
    system_prompt = f"""
    You are JAZ Creativity Studio, a safe creative assistant for children.

    Child:
    Name: {child.name}
    Age: {child.age}
    Interests: {child.interests}

    Project type:
    {project_type}

    Rules:
    - Be child-safe and age-appropriate.
    - Encourage imagination, kindness, learning, and creativity.
    - Do not create adult, sexual, violent, harmful, or unsafe content.
    - Keep the output simple and helpful.
    - Give the child something they can build on.
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content


@router.post("/generate")
def generate_creativity(data: CreativeAIRequest, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if data.project_type not in ALLOWED_PROJECT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid project_type. Use one of: {ALLOWED_PROJECT_TYPES}"
        )

    ai_output = generate_creative_response(
        child=child,
        project_type=data.project_type,
        prompt=data.prompt
    )

    return {
        "child": child.name,
        "project_type": data.project_type,
        "prompt": data.prompt,
        "ai_output": ai_output
    }


@router.post("/projects")
def save_creative_project(
    data: CreativeProjectCreate,
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if data.project_type not in ALLOWED_PROJECT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid project_type. Use one of: {ALLOWED_PROJECT_TYPES}"
        )

    stars = 5

    project = CreativeProject(
        child_id=child.id,
        title=data.title,
        project_type=data.project_type,
        prompt=data.prompt,
        child_notes=data.child_notes,
        stars_earned=stars,
        status="saved"
    )

    child.wisdom_stars += stars
    child.level = calculate_child_level(child.wisdom_stars)
    child.rating = calculate_rating(child.wisdom_stars)

    activity = LearningActivity(
        child_id=child.id,
        topic="Creativity Studio",
        activity_type="creative_project",
        summary=f"Created {data.project_type}: {data.title}",
        stars_earned=stars
    )

    db.add(project)
    db.add(activity)
    db.commit()
    db.refresh(project)

    return {
        "message": "Creative project saved",
        "project": project,
        "stars_earned": stars,
        "total_wisdom_stars": child.wisdom_stars,
        "level": child.level,
        "rating": child.rating
    }


@router.get("/projects/{child_id}")
def get_child_projects(child_id: int, db: Session = Depends(get_db)):
    projects = db.query(CreativeProject).filter(
        CreativeProject.child_id == child_id
    ).order_by(CreativeProject.created_at.desc()).all()

    return {
        "child_id": child_id,
        "projects": projects
    }