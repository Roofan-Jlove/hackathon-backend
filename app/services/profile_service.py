from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models import UserProfile


class ProfileService:
    """Service for user profile operations."""

    @staticmethod
    def create_profile(db: Session, user_id: UUID, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Create a user profile.

        Args:
            db: Database session
            user_id: User ID
            profile_data: Profile data dictionary

        Returns:
            UserProfile object

        Raises:
            HTTPException: If profile already exists
        """
        # Check if profile exists
        existing_profile = db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()

        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile already exists"
            )

        # Create profile
        profile = UserProfile(
            user_id=user_id,
            **profile_data
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile

    @staticmethod
    def get_profile(db: Session, user_id: UUID) -> Optional[UserProfile]:
        """
        Get a user's profile.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            UserProfile object or None
        """
        return db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()

    @staticmethod
    def update_profile(db: Session, user_id: UUID,
                      profile_data: Dict[str, Any]) -> UserProfile:
        """
        Update a user's profile.

        Args:
            db: Database session
            user_id: User ID
            profile_data: Profile data to update

        Returns:
            Updated UserProfile object

        Raises:
            HTTPException: If profile doesn't exist
        """
        profile = ProfileService.get_profile(db, user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Update fields
        for key, value in profile_data.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)

        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)

        return profile
