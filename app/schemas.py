from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Profile Schemas
class ProfileCreate(BaseModel):
    programming_experience: Optional[str] = None
    python_proficiency: Optional[str] = None
    ros_experience: Optional[str] = None
    ai_ml_experience: Optional[str] = None
    robotics_hardware_experience: Optional[str] = None
    sensor_integration: Optional[str] = None
    electronics_knowledge: Optional[str] = None
    primary_interests: Optional[List[str]] = []
    time_commitment: Optional[str] = None


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    programming_experience: Optional[str]
    python_proficiency: Optional[str]
    ros_experience: Optional[str]
    ai_ml_experience: Optional[str]
    robotics_hardware_experience: Optional[str]
    sensor_integration: Optional[str]
    electronics_knowledge: Optional[str]
    primary_interests: Optional[List[str]]
    time_commitment: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Combined signup schema
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    profile: Optional[ProfileCreate] = None


class SignupResponse(BaseModel):
    user: UserResponse
    profile: Optional[ProfileResponse]
    token: str
    token_type: str = "bearer"


# Signin schemas
class SigninRequest(BaseModel):
    email: EmailStr
    password: str


class SigninResponse(BaseModel):
    user: UserResponse
    profile: Optional[ProfileResponse]
    token: str
    token_type: str = "bearer"


# Session schema
class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
