from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models import (
    Parent,
    Child,
    ParentSafetySetting,
    InternetActivity
)
from app.schemas import ParentSafetySettingCreate, SafetyClassifyRequest
from app.safety_classifier import classify_internet_activity

router = APIRouter()


@router.post("/classify")
def classify_safety_activity(data: SafetyClassifyRequest):
    label = classify_internet_activity(
        website_or_app=data.website_or_app,
        url=data.url,
        summary=data.summary
    )

    return {
        "website_or_app": data.website_or_app,
        "url": data.url,
        "summary": data.summary,
        "classification": label
    }


@router.post("/settings")
def create_or_update_safety_settings(
    data: ParentSafetySettingCreate,
    db: Session = Depends(get_db)
):
    parent = db.query(Parent).filter(Parent.id == data.parent_id).first()
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if child.parent_id != parent.id:
        raise HTTPException(status_code=403, detail="Child does not belong to this parent")

    setting = db.query(ParentSafetySetting).filter(
        ParentSafetySetting.parent_id == parent.id,
        ParentSafetySetting.child_id == child.id
    ).first()

    if setting:
        setting.daily_screen_time_limit_minutes = data.daily_screen_time_limit_minutes
        setting.child_safe_mode = data.child_safe_mode
        setting.internet_monitoring_enabled = data.internet_monitoring_enabled
        setting.ai_chat_monitoring_enabled = data.ai_chat_monitoring_enabled
        setting.blocked_categories = data.blocked_categories
        setting.allowed_categories = data.allowed_categories
    else:
        setting = ParentSafetySetting(
            parent_id=data.parent_id,
            child_id=data.child_id,
            daily_screen_time_limit_minutes=data.daily_screen_time_limit_minutes,
            child_safe_mode=data.child_safe_mode,
            internet_monitoring_enabled=data.internet_monitoring_enabled,
            ai_chat_monitoring_enabled=data.ai_chat_monitoring_enabled,
            blocked_categories=data.blocked_categories,
            allowed_categories=data.allowed_categories
        )
        db.add(setting)

    db.commit()
    db.refresh(setting)

    return {
        "message": "Safety settings saved",
        "settings": setting
    }


@router.get("/settings/{child_id}")
def get_safety_settings(child_id: int, db: Session = Depends(get_db)):
    setting = db.query(ParentSafetySetting).filter(
        ParentSafetySetting.child_id == child_id
    ).first()

    if not setting:
        raise HTTPException(status_code=404, detail="No safety settings found")

    return setting


@router.get("/screen-time/{child_id}")
def check_screen_time_status(child_id: int, db: Session = Depends(get_db)):
    setting = db.query(ParentSafetySetting).filter(
        ParentSafetySetting.child_id == child_id
    ).first()

    if not setting:
        raise HTTPException(status_code=404, detail="No safety settings found")

    start_date = datetime.utcnow() - timedelta(days=1)

    activities = db.query(InternetActivity).filter(
        InternetActivity.child_id == child_id,
        InternetActivity.created_at >= start_date
    ).all()

    used_minutes = sum(a.duration_minutes for a in activities)
    limit_minutes = setting.daily_screen_time_limit_minutes

    return {
        "child_id": child_id,
        "used_minutes_today": used_minutes,
        "daily_limit_minutes": limit_minutes,
        "remaining_minutes": max(0, limit_minutes - used_minutes),
        "limit_reached": used_minutes >= limit_minutes
    }


@router.get("/category-check/{child_id}")
def check_category_allowed(
    child_id: int,
    category: str,
    db: Session = Depends(get_db)
):
    setting = db.query(ParentSafetySetting).filter(
        ParentSafetySetting.child_id == child_id
    ).first()

    if not setting:
        raise HTTPException(status_code=404, detail="No safety settings found")

    blocked = [c.strip().lower() for c in setting.blocked_categories.split(",")]
    allowed = [c.strip().lower() for c in setting.allowed_categories.split(",")]

    category_clean = category.strip().lower()

    if category_clean in blocked:
        return {
            "child_id": child_id,
            "category": category,
            "allowed": False,
            "reason": "Category is blocked by parent"
        }

    if category_clean in allowed:
        return {
            "child_id": child_id,
            "category": category,
            "allowed": True,
            "reason": "Category is allowed"
        }

    if setting.child_safe_mode == "strict":
        return {
            "child_id": child_id,
            "category": category,
            "allowed": False,
            "reason": "Strict mode blocks unknown categories"
        }

    return {
        "child_id": child_id,
        "category": category,
        "allowed": True,
        "reason": "Balanced mode allows unknown category"
    }
