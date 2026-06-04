from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Child
from app.schemas import ChildCreate, ChildResponse, ChildUpdate

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


@router.get("/profile/{child_id}", response_model=ChildResponse)
def get_child_profile(child_id: int, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    return child


@router.put("/{child_id}", response_model=ChildResponse)
def update_child(
    child_id: int,
    data: ChildUpdate,
    db: Session = Depends(get_db)
):
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    if data.name is not None:
        child.name = data.name

    if data.age is not None:
        child.age = data.age

    if data.interests is not None:
        child.interests = data.interests

    if data.avatar is not None:
        child.avatar = data.avatar

    db.commit()
    db.refresh(child)

    return child


@router.get("/{parent_id}")
def get_children(parent_id: int, db: Session = Depends(get_db)):
    return db.query(Child).filter(Child.parent_id == parent_id).all()
