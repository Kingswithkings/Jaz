from pydantic import BaseModel, EmailStr
from typing import Optional

class ParentCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

class ParentLogin(BaseModel):
    email: EmailStr
    password: str

class ChildCreate(BaseModel):
    name: str
    age: int
    interests: Optional[str] = None
    avatar: Optional[str] = None

class ChildResponse(BaseModel):
    id: int
    name: str
    age: int
    interests: Optional[str]
    wisdom_stars: int
    level: str
    rating: int

    class Config:
        from_attributes = True

class AIChatRequest(BaseModel):
    child_id: int
    message: str

class AIChatResponse(BaseModel):
    response: str


class LearningPostCreate(BaseModel):
    title: str
    content: str
    category: str
    age_min: int = 5
    age_max: int = 15
    stars_reward: int = 2

class LearningPostResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    age_min: int
    age_max: int
    stars_reward: int

    class Config:
        from_attributes = True


class SocialPostCreate(BaseModel):
    child_id: int
    title: str
    content: str
    media_url: Optional[str] = None
    category: str = "general"


class SocialPostResponse(BaseModel):
    id: int
    child_id: int
    title: str
    content: str
    media_url: Optional[str]
    category: str
    status: str
    stars_received: int

    class Config:
        from_attributes = True


class BadgeCreate(BaseModel):
    badge: str

class ReportRequest(BaseModel):
    parent_id: int
    child_id: int
    report_type: str = "daily"
    send_email: bool = False

class InternetActivityCreate(BaseModel):
    child_id: int
    website_or_app: str
    url: Optional[str] = None
    category: str = "unknown"
    duration_minutes: int = 0
    learning_value: str = "neutral"
    summary: Optional[str] = None


class CommunityCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "learning"
    age_min: int = 5
    age_max: int = 15


class CommunityJoinRequest(BaseModel):
    child_id: int


class CommunityPostCreate(BaseModel):
    child_id: int
    content: str

class CreativeProjectCreate(BaseModel):
    child_id: int
    title: str
    project_type: str
    prompt: Optional[str] = None
    child_notes: Optional[str] = None


class CreativeAIRequest(BaseModel):
    child_id: int
    project_type: str
    prompt: str

class HomeworkHelpRequest(BaseModel):
    child_id: int
    subject: str
    question: str

class QuizGenerateRequest(BaseModel):
    child_id: int
    topic: str
    difficulty: str = "easy"
    number_of_questions: int = 5


class QuizSubmitRequest(BaseModel):
    child_id: int
    quiz_id: int
    score: int