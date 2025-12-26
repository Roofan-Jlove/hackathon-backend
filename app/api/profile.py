from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.dependencies import get_current_user
from app.services.profile_service import ProfileService
from app.schemas import ProfileCreate, ProfileResponse
from app.models import User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's profile.

    Requires authentication.
    """
    profile = ProfileService.get_profile(db, current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return ProfileResponse.model_validate(profile)


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a profile for the current user.

    Requires authentication.
    """
    profile_dict = profile_data.model_dump(exclude_none=True)
    profile = ProfileService.create_profile(
        db=db,
        user_id=current_user.id,
        profile_data=profile_dict
    )

    return ProfileResponse.model_validate(profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile.

    Requires authentication.
    """
    profile_dict = profile_data.model_dump(exclude_none=True)
    profile = ProfileService.update_profile(
        db=db,
        user_id=current_user.id,
        profile_data=profile_dict
    )

    return ProfileResponse.model_validate(profile)
