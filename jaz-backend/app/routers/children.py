from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Child
from app.schemas import ChildCreate, ChildResponse

router = APIRouter()

@router.post("", response_model=ChildResponse)
def create_child(data: ChildCreate, parent_id: int, db: Session = Depends(get_db)):
    child = Child(
        parent_id=parent_id,
        name=data.name,
        age=data.age,
        interests=data.interests,
        avatar=data.avatar
    )

    db.add(child)
    db.commit()
    db.refresh(child)

    return child


@router.get("/{parent_id}")
def get_children(parent_id: int, db: Session = Depends(get_db)):
    return db.query(Child).filter(Child.parent_id == parent_id).all()
