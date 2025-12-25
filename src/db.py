import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Default to local postgres if not set (for docker)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/autismyvr")

engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import models here to avoid circular changes
    from src.models import ChatSession, Interaction
    Base.metadata.create_all(bind=engine)
