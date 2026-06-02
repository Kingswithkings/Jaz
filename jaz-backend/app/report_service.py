import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from dotenv import load_dotenv

load_dotenv()

REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def get_report_date_range(report_type: str):
    now = datetime.utcnow()

    if report_type == "weekly":
        start_date = now - timedelta(days=7)
    else:
        start_date = now - timedelta(days=1)

    return start_date, now


def ensure_space(pdf, y, height, needed=80):
    if y < needed:
        pdf.showPage()
        pdf.setFont("Helvetica", 10)
        return height - 50

    return y


def create_parent_pdf_report(
    parent_name: str,
    parent_email: str,
    child_name: str,
    report_type: str,
    activities: list,
    chats: list,
    social_posts: list,
    internet_activities: list,
    total_stars: int
):
    safe_child_name = "".join(
        char if char.isalnum() or char in ("-", "_") else "_"
        for char in child_name.strip()
    ) or "child"
    filename = f"{safe_child_name}_{report_type}_report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
    file_path = os.path.join(REPORTS_DIR, filename)

    pdf = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "JAZ Parent Monitoring Report")

    y -= 30
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Parent: {parent_name}")
    y -= 18
    pdf.drawString(50, y, f"Email: {parent_email}")
    y -= 18
    pdf.drawString(50, y, f"Child: {child_name}")
    y -= 18
    pdf.drawString(50, y, f"Report Type: {report_type.title()}")
    y -= 18
    pdf.drawString(50, y, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

    y -= 35
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Growth Summary")

    y -= 25
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Total Wisdom Stars: {total_stars}")
    y -= 18
    pdf.drawString(50, y, f"Learning Activities: {len(activities)}")
    y -= 18
    pdf.drawString(50, y, f"AI Conversations: {len(chats)}")
    y -= 18
    pdf.drawString(50, y, f"Creative/Social Posts: {len(social_posts)}")
    y -= 18

    total_internet_minutes = sum(a.duration_minutes for a in internet_activities)
    educational_minutes = sum(
        a.duration_minutes for a in internet_activities
        if a.learning_value == "educational"
    )
    unsafe_count = len([
        a for a in internet_activities
        if a.learning_value == "unsafe"
    ])

    pdf.drawString(50, y, f"Internet Time: {total_internet_minutes} minutes")
    y -= 18
    pdf.drawString(50, y, f"Educational Internet Time: {educational_minutes} minutes")
    y -= 18
    pdf.drawString(50, y, f"Unsafe/Flagged Internet Activities: {unsafe_count}")

    y -= 35
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "What Your Child Learned")

    pdf.setFont("Helvetica", 10)

    if not activities:
        y -= 20
        pdf.drawString(50, y, "No learning activity recorded in this period.")
    else:
        for activity in activities[:10]:
            y -= 18
            text = f"- {activity.topic}: {activity.summary} (+{activity.stars_earned} stars)"
            pdf.drawString(50, y, text[:95])

            y = ensure_space(pdf, y, height)

    y -= 35
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "AI Conversation Highlights")

    pdf.setFont("Helvetica", 10)

    if not chats:
        y -= 20
        pdf.drawString(50, y, "No AI conversations recorded in this period.")
    else:
        for chat in chats[:8]:
            y -= 18
            pdf.drawString(50, y, f"- Child asked: {chat.message[:90]}")

            y = ensure_space(pdf, y, height)

    y -= 35
    y = ensure_space(pdf, y, height, needed=120)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Internet Consumption Summary")

    pdf.setFont("Helvetica", 10)

    if not internet_activities:
        y -= 20
        pdf.drawString(50, y, "No internet activity recorded in this period.")
    else:
        for item in internet_activities[:10]:
            y -= 18
            text = (
                f"- {item.website_or_app}: {item.duration_minutes} mins, "
                f"{item.category}, {item.learning_value}"
            )
            pdf.drawString(50, y, text[:95])

            if item.summary:
                y -= 15
                pdf.drawString(70, y, f"Summary: {item.summary[:85]}")

            y = ensure_space(pdf, y, height)

    y -= 35
    y = ensure_space(pdf, y, height, needed=100)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Parent Insight")

    y -= 20
    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        50,
        y,
        "Your child is building learning confidence through safe conversations, creativity, and guided activities."
    )

    pdf.save()

    return file_path


def send_report_email(parent_email: str, child_name: str, report_type: str, file_path: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_host, smtp_email, smtp_password]):
        raise RuntimeError(
            "SMTP_HOST, SMTP_EMAIL, and SMTP_PASSWORD must be set to send reports."
        )

    if not Path(file_path).exists():
        raise RuntimeError(f"Report file does not exist: {file_path}")

    msg = EmailMessage()
    msg["Subject"] = f"JAZ {report_type.title()} Report for {child_name}"
    msg["From"] = smtp_email
    msg["To"] = parent_email

    msg.set_content(
        f"""
Hello,

Attached is the {report_type} JAZ learning and safety report for {child_name}.

This report includes:
- Learning activities
- AI conversations
- Creativity/social activity
- Wisdom Stars progress

JAZ — Building Joyful and Wise Generations.
"""
    )

    with open(file_path, "rb") as file:
        msg.add_attachment(
            file.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(file_path)
        )

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_email, smtp_password)
            smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError(
            "SMTP authentication failed. For Gmail, use a Google App Password "
            "instead of your normal account password."
        ) from exc
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"SMTP email delivery failed: {exc}") from exc

    return True
