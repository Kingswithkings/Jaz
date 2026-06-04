from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables
from app.routers import auth, children, ai, parent_dashboard, feed, social, internet, communities, creativity, homework, quiz, safety, goals, learning_path
create_tables()

app = FastAPI(
    title="JAZ API",
    description="AI-powered child development platform by 1stKings Ltd",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(children.router, prefix="/children", tags=["Children"])
app.include_router(ai.router, prefix="/ai", tags=["AI Companion"])
app.include_router(parent_dashboard.router, prefix="/parents", tags=["Parent Dashboard"])
app.include_router(feed.router, prefix="/feed", tags=["Learning Feed"])
app.include_router(social.router, prefix="/social", tags=["Child-Safe Social"])
app.include_router(internet.router, prefix="/internet", tags=["Internet Monitoring"])
app.include_router(communities.router, prefix="/communities", tags=["Safe Communities"])
app.include_router(creativity.router, prefix="/creativity", tags=["Creativity Studio"])
app.include_router(homework.router, prefix="/homework", tags=["Homework Helper"])
app.include_router(quiz.router, prefix="/quiz", tags=["AI Quiz Generator"])
app.include_router(safety.router, prefix="/safety", tags=["Parent Safety Controls"])
app.include_router(goals.router, prefix="/goals", tags=["Learning Goals"])
app.include_router(learning_path.router, prefix="/learning-path", tags=["AI Learning Path"])

@app.get("/")
def home():
    return {
        "message": "JAZ API is running",
        "tagline": "Building Joyful and Wise Generations"
    }
