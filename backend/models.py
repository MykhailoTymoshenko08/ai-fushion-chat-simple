from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProviderResponse(Base):
    __tablename__ = "provider_responses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # openai, groq, deepseek, gemini
    content = Column(Text, nullable=False)
    response_time = Column(Integer)  # in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False)
    score = Column(Integer, nullable=False)  # 1 for like, -1 for dislike
    created_at = Column(DateTime, default=datetime.utcnow)