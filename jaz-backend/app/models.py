from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    children = relationship("Child", back_populates="parent")


class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"))
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    interests = Column(Text)
    avatar = Column(String, nullable=True)
    wisdom_stars = Column(Integer, default=0)
    level = Column(String, default="Explorer")
    rating = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("Parent", back_populates="children")


class LearningActivity(Base):
    __tablename__ = "learning_activities"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    topic = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)
    summary = Column(Text)
    stars_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AIChatLog(Base):
    __tablename__ = "ai_chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class LearningPost(Base):
    __tablename__ = "learning_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    age_min = Column(Integer, default=5)
    age_max = Column(Integer, default=15)
    stars_reward = Column(Integer, default=2)
    created_at = Column(DateTime, default=datetime.utcnow)


class SocialPost(Base):
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    category = Column(String, default="general")
    status = Column(String, default="pending_review")
    stars_received = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class PostBadge(Base):
    __tablename__ = "post_badges"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("social_posts.id"))
    badge = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ParentReport(Base):
    __tablename__ = "parent_reports"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"))
    child_id = Column(Integer, ForeignKey("children.id"))
    report_type = Column(String, nullable=False)  # daily or weekly
    summary = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class InternetActivity(Base):
    __tablename__ = "internet_activities"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    website_or_app = Column(String, nullable=False)
    url = Column(String, nullable=True)
    category = Column(String, default="unknown")
    duration_minutes = Column(Integer, default=0)
    learning_value = Column(String, default="neutral")  # educational, neutral, unsafe
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Community(Base):
    __tablename__ = "communities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, default="learning")
    age_min = Column(Integer, default=5)
    age_max = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)


class CommunityMember(Base):
    __tablename__ = "community_members"

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("communities.id"))
    child_id = Column(Integer, ForeignKey("children.id"))
    joined_at = Column(DateTime, default=datetime.utcnow)


class CommunityPost(Base):
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("communities.id"))
    child_id = Column(Integer, ForeignKey("children.id"))
    content = Column(Text, nullable=False)
    status = Column(String, default="pending_review")
    created_at = Column(DateTime, default=datetime.utcnow)

class CreativeProject(Base):
    __tablename__ = "creative_projects"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    title = Column(String, nullable=False)
    project_type = Column(String, nullable=False)  # story, poem, drawing, comic, music, bible_reflection
    prompt = Column(Text, nullable=True)
    ai_output = Column(Text, nullable=True)
    child_notes = Column(Text, nullable=True)
    status = Column(String, default="draft")
    stars_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class HomeworkSession(Base):
    __tablename__ = "homework_sessions"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    subject = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    ai_explanation = Column(Text, nullable=False)
    learning_points = Column(Text, nullable=True)
    stars_earned = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    topic = Column(String, nullable=False)
    difficulty = Column(String, default="easy")
    questions = Column(Text, nullable=False)
    score = Column(Integer, default=0)
    stars_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)