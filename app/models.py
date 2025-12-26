from sqlalchemy import create_engine, Column, String, UUID as SQL_UUID, JSON, DateTime, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr
from typing import Dict, Optional

# SQLAlchemy Base
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Integer, default=True, nullable=False)
    is_verified = Column(Integer, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    software_background = Column(JSON, default=lambda: {})
    hardware_background = Column(JSON, default=lambda: {})

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user")

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(SQL_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Software background
    programming_experience = Column(String(50), nullable=True)
    python_proficiency = Column(String(50), nullable=True)
    ros_experience = Column(String(50), nullable=True)
    ai_ml_experience = Column(String(50), nullable=True)

    # Hardware background
    robotics_hardware_experience = Column(String(50), nullable=True)
    sensor_integration = Column(String(50), nullable=True)
    electronics_knowledge = Column(String(50), nullable=True)

    # Learning goals
    primary_interests = Column(JSON, nullable=True)
    time_commitment = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id='{self.user_id}')>"

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(SQL_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f"<Session(user_id='{self.user_id}', expires_at='{self.expires_at}')>"

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(SQL_UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    title = Column(String, nullable=True)  # Optional title for the conversation
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to messages
    messages = relationship("Message", back_populates="conversation")
    user = relationship("User", back_populates="conversations")

class Message(Base):
    __tablename__ = 'messages'

    id = Column(SQL_UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(SQL_UUID(as_uuid=True), ForeignKey('conversations.id'), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    additional_data = Column(JSON, default=lambda: {})  # Store additional metadata about the message

    conversation = relationship("Conversation", back_populates="messages")

# Pydantic models for API request/response validation
class UserProfileBase(BaseModel):
    email: EmailStr
    software_background: Dict[str, str] = {}
    hardware_background: Dict[str, str] = {}

class UserProfileCreate(UserProfileBase):
    # Passwords handled by better-auth, not stored here
    pass

class UserProfileDisplay(UserProfileBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True # for SQLAlchemy integration with Pydantic

class MessageBase(BaseModel):
    role: str
    content: str
    additional_data: Optional[Dict] = {}

class MessageCreate(MessageBase):
    conversation_id: UUID

class MessageDisplay(MessageBase):
    id: UUID
    conversation_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    user_id: Optional[UUID] = None

class ConversationDisplay(ConversationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    messages: list[MessageDisplay] = []

    class Config:
        from_attributes = True
