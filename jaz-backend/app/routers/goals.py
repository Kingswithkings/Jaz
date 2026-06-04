from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Child, LearningGoal
from app.schemas import LearningGoalCreate, LearningGoalUpdate

router = APIRouter()


@router.post("/")
def create_learning_goal(
    data: LearningGoalCreate,
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == data.child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    goal = LearningGoal(
        child_id=data.child_id,
        title=data.title,
        description=data.description,
        category=data.category,
        target_stars=data.target_stars
    )

    db.add(goal)
    db.commit()
    db.refresh(goal)

    return goal


@router.get("/{child_id}")
def get_child_goals(child_id: int, db: Session = Depends(get_db)):
    goals = db.query(LearningGoal).filter(
        LearningGoal.child_id == child_id
    ).order_by(LearningGoal.created_at.desc()).all()

    return {
        "child_id": child_id,
        "goals": goals
    }


@router.put("/{goal_id}")
def update_learning_goal(
    goal_id: int,
    data: LearningGoalUpdate,
    db: Session = Depends(get_db)
):
    goal = db.query(LearningGoal).filter(LearningGoal.id == goal_id).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Learning goal not found")

    if data.title is not None:
        goal.title = data.title

    if data.description is not None:
        goal.description = data.description

    if data.category is not None:
        goal.category = data.category

    if data.target_stars is not None:
        goal.target_stars = data.target_stars

    if data.current_stars is not None:
        goal.current_stars = data.current_stars

    if data.status is not None:
        goal.status = data.status

    if goal.current_stars >= goal.target_stars:
        goal.status = "completed"

    db.commit()
    db.refresh(goal)

    return goal


@router.delete("/{goal_id}")
def delete_learning_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(LearningGoal).filter(LearningGoal.id == goal_id).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Learning goal not found")

    db.delete(goal)
    db.commit()

    return {
        "message": "Learning goal deleted"
    }