from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import create_token, hash_password, verify_password
from app.database import get_db
from app.models import Parent
from app.schemas import ParentCreate, ParentLogin

router = APIRouter()


@router.post("/register")
def register_parent(data: ParentCreate, db: Session = Depends(get_db)):
    existing = db.query(Parent).filter(Parent.email == data.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    parent = Parent(
        full_name=data.full_name,
        email=data.email,
        password_hash=hash_password(data.password)
    )

    db.add(parent)
    db.commit()
    db.refresh(parent)

    token = create_token({"parent_id": parent.id, "email": parent.email})

    return {
        "message": "Parent account created successfully",
        "token": token,
        "parent_id": parent.id
    }


@router.post("/login")
def login_parent(data: ParentLogin, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.email == data.email).first()

    if not parent or not verify_password(data.password, parent.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"parent_id": parent.id, "email": parent.email})

    return {
        "message": "Login successful",
        "token": token,
        "parent_id": parent.id
    }
