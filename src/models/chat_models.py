from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index, Enum
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.db import Base, engine
import enum

def get_uuid_column():
    """Return appropriate UUID column type based on database."""
    if engine.dialect.name == 'postgresql':
        return Column(PostgresUUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    else:
        # SQLite doesn't support UUID natively, use String
        return Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False, index=True)

class ChatMode(enum.Enum):
    TEXT = "text"
    AUDIO = "audio"

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_uuid = get_uuid_column()
    firebase_uid = Column(String(128), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    mode = Column(Enum(ChatMode), nullable=False, default=ChatMode.TEXT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_firebase_uid', 'firebase_uid'),
        Index('idx_session_uuid', 'session_uuid'),
        Index('idx_mode', 'mode'),
    )
    
    interactions = relationship("Interaction", back_populates="session", cascade="all, delete-orphan")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    audio_response_url = Column(String(500), nullable=True)
    liveportrait_data = Column(Text, nullable=True)
    model_used = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="interactions")

