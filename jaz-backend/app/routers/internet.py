from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Child, InternetActivity, Parent, ParentSafetySetting
from app.schemas import InternetActivityCreate
from app.safety_classifier import classify_internet_activity
from app.report_service import send_parent_safety_alert

router = APIRouter()


@router.post("/track")
def track_internet_activity(
    data: InternetActivityCreate,
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    parent = db.query(Parent).filter(Parent.id == child.parent_id).first()

    classified_value = classify_internet_activity(
        website_or_app=data.website_or_app,
        url=data.url,
        summary=data.summary
    )

    activity = InternetActivity(
        child_id=data.child_id,
        website_or_app=data.website_or_app,
        url=data.url,
        category=data.category,
        duration_minutes=data.duration_minutes,
        learning_value=classified_value,
        summary=data.summary
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    alert_sent = False

    setting = db.query(ParentSafetySetting).filter(
        ParentSafetySetting.child_id == child.id
    ).first()

    if (
        classified_value == "unsafe"
        and parent
        and setting
        and setting.internet_monitoring_enabled == "yes"
    ):
        alert_sent = send_parent_safety_alert(
            parent_email=parent.email,
            parent_name=parent.full_name,
            child_name=child.name,
            website_or_app=data.website_or_app,
            url=data.url,
            category=data.category,
            summary=data.summary
        )

    return {
        "message": "Internet activity recorded",
        "activity_id": activity.id,
        "ai_classification": classified_value,
        "parent_alert_sent": alert_sent
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
