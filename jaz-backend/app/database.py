from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Add it to jaz-backend/.env.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        raise RuntimeError(
            "Could not connect to the database. Start PostgreSQL and make sure "
            "DATABASE_URL in jaz-backend/.env points to the running database."
        ) from None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
