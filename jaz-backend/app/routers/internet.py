from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Child, InternetActivity
from app.schemas import InternetActivityCreate

router = APIRouter()


@router.post("/track")
def track_internet_activity(
    data: InternetActivityCreate,
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    activity = InternetActivity(
        child_id=data.child_id,
        website_or_app=data.website_or_app,
        url=data.url,
        category=data.category,
        duration_minutes=data.duration_minutes,
        learning_value=data.learning_value,
        summary=data.summary
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return {
        "message": "Internet activity recorded",
        "activity_id": activity.id
    }


@router.get("/{child_id}/daily")
def get_daily_internet_report(child_id: int, db: Session = Depends(get_db)):
    start_date = datetime.utcnow() - timedelta(days=1)

    activities = db.query(InternetActivity).filter(
        InternetActivity.child_id == child_id,
        InternetActivity.created_at >= start_date
    ).all()

    total_minutes = sum(a.duration_minutes for a in activities)
    educational_minutes = sum(
        a.duration_minutes for a in activities
        if a.learning_value == "educational"
    )

    return {
        "child_id": child_id,
        "period": "daily",
        "total_minutes": total_minutes,
        "educational_minutes": educational_minutes,
        "activities": activities
    }


@router.get("/{child_id}/weekly")
def get_weekly_internet_report(child_id: int, db: Session = Depends(get_db)):
    start_date = datetime.utcnow() - timedelta(days=7)

    activities = db.query(InternetActivity).filter(
        InternetActivity.child_id == child_id,
        InternetActivity.created_at >= start_date
    ).all()

    total_minutes = sum(a.duration_minutes for a in activities)
    educational_minutes = sum(
        a.duration_minutes for a in activities
        if a.learning_value == "educational"
    )

    unsafe_count = len([
        a for a in activities if a.learning_value == "unsafe"
    ])

    return {
        "child_id": child_id,
        "period": "weekly",
        "total_minutes": total_minutes,
        "educational_minutes": educational_minutes,
        "unsafe_activity_count": unsafe_count,
        "activities": activities
    }