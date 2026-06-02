from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Parent,
    Child,
    LearningActivity,
    AIChatLog,
    SocialPost,
    ParentReport,
    InternetActivity
)
from app.schemas import ReportRequest
from app.report_service import (
    get_report_date_range,
    create_parent_pdf_report,
    send_report_email
)

router = APIRouter()

@router.get("/{parent_id}/dashboard")
def parent_dashboard(parent_id: int, db: Session = Depends(get_db)):
    children = db.query(Child).filter(Child.parent_id == parent_id).all()

    if not children:
        raise HTTPException(status_code=404, detail="No children found")

    data = []

    for child in children:
        activities = db.query(LearningActivity).filter(
            LearningActivity.child_id == child.id
        ).all()

        chats = db.query(AIChatLog).filter(
            AIChatLog.child_id == child.id
        ).all()

        data.append({
            "child_id": child.id,
            "name": child.name,
            "age": child.age,
            "level": child.level,
            "rating": child.rating,
            "wisdom_stars": child.wisdom_stars,
            "total_learning_activities": len(activities),
            "total_ai_conversations": len(chats),
            "recent_activities": activities[-5:]
        })

    return {
        "parent_id": parent_id,
        "children": data
    }


@router.get("/{parent_id}/summary")
def get_parent_summary(parent_id: int, db: Session = Depends(get_db)):
    children = db.query(Child).filter(Child.parent_id == parent_id).all()

    if not children:
        raise HTTPException(status_code=404, detail="No children found")

    dashboard = []

    for child in children:
        activities = db.query(LearningActivity).filter(
            LearningActivity.child_id == child.id
        ).all()

        chats = db.query(AIChatLog).filter(
            AIChatLog.child_id == child.id
        ).all()

        internet = db.query(InternetActivity).filter(
            InternetActivity.child_id == child.id
        ).all()

        total_minutes = sum(i.duration_minutes for i in internet)
        educational_minutes = sum(
            i.duration_minutes for i in internet
            if i.learning_value == "educational"
        )
        unsafe_count = len([
            i for i in internet
            if i.learning_value == "unsafe"
        ])

        dashboard.append({
            "child_id": child.id,
            "name": child.name,
            "age": child.age,
            "level": child.level,
            "rating": child.rating,
            "wisdom_stars": child.wisdom_stars,
            "total_learning_activities": len(activities),
            "total_ai_conversations": len(chats),
            "total_internet_minutes": total_minutes,
            "educational_minutes": educational_minutes,
            "unsafe_activity_count": unsafe_count,
            "learning_score": round(
                (educational_minutes / total_minutes) * 100, 2
            ) if total_minutes > 0 else 0
        })

    return {
        "parent_id": parent_id,
        "children": dashboard
    }


@router.post("/reports/generate")
def generate_parent_report(data: ReportRequest, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.id == data.parent_id).first()
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if child.parent_id != parent.id:
        raise HTTPException(
            status_code=403,
            detail="This child does not belong to this parent"
        )

    if data.report_type not in ["daily", "weekly"]:
        raise HTTPException(
            status_code=400,
            detail="report_type must be daily or weekly"
        )

    start_date, end_date = get_report_date_range(data.report_type)

    activities = db.query(LearningActivity).filter(
        LearningActivity.child_id == child.id,
        LearningActivity.created_at >= start_date,
        LearningActivity.created_at <= end_date
    ).all()

    chats = db.query(AIChatLog).filter(
        AIChatLog.child_id == child.id,
        AIChatLog.created_at >= start_date,
        AIChatLog.created_at <= end_date
    ).all()

    social_posts = db.query(SocialPost).filter(
        SocialPost.child_id == child.id,
        SocialPost.created_at >= start_date,
        SocialPost.created_at <= end_date
    ).all()

    internet_activities = db.query(InternetActivity).filter(
        InternetActivity.child_id == child.id,
        InternetActivity.created_at >= start_date,
        InternetActivity.created_at <= end_date
    ).all()

    file_path = create_parent_pdf_report(
        parent_name=parent.full_name,
        parent_email=parent.email,
        child_name=child.name,
        report_type=data.report_type,
        activities=activities,
        chats=chats,
        social_posts=social_posts,
        internet_activities=internet_activities,
        total_stars=child.wisdom_stars
    )

    report = ParentReport(
        parent_id=parent.id,
        child_id=child.id,
        report_type=data.report_type,
        summary=f"{data.report_type.title()} report generated for {child.name}",
        file_path=file_path
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    email_sent = False
    email_error = None

    if data.send_email:
        try:
            send_report_email(
                parent_email=parent.email,
                child_name=child.name,
                report_type=data.report_type,
                file_path=file_path
            )
            email_sent = True
        except RuntimeError as exc:
            email_error = str(exc)

    return {
        "message": "Report generated successfully",
        "report_id": report.id,
        "report_type": data.report_type,
        "child": child.name,
        "download_url": f"/parents/reports/download/{report.id}",
        "email_sent": email_sent,
        "email_error": email_error
    }


@router.get("/reports/download/{report_id}")
def download_parent_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(ParentReport).filter(ParentReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.file_path:
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=report.file_path,
        filename=report.file_path.split("/")[-1],
        media_type="application/pdf"
    )
