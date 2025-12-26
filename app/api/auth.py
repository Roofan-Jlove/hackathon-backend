from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.config import get_db
from app.core.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService
from app.schemas import (
    SignupRequest, SignupResponse,
    SigninRequest, SigninResponse,
    UserResponse, ProfileResponse
)
from app.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user with optional profile data.

    - **email**: Valid email address
    - **password**: Minimum 8 characters, must contain uppercase and digit
    - **profile**: Optional profile information
    """
    # Create user
    user, token = AuthService.signup(
        db=db,
        email=signup_data.email,
        password=signup_data.password
    )

    # Create profile if provided
    profile = None
    if signup_data.profile:
        profile_dict = signup_data.profile.model_dump(exclude_none=True)
        profile = ProfileService.create_profile(
            db=db,
            user_id=user.id,
            profile_data=profile_dict
        )

    return SignupResponse(
        user=UserResponse.model_validate(user),
        profile=ProfileResponse.model_validate(profile) if profile else None,
        token=token
    )


@router.post("/signin", response_model=SigninResponse)
async def signin(
    signin_data: SigninRequest,
    db: Session = Depends(get_db)
):
    """
    Sign in an existing user.

    - **email**: Registered email address
    - **password**: User password
    """
    # Authenticate user
    user, token = AuthService.signin(
        db=db,
        email=signin_data.email,
        password=signin_data.password
    )

    # Get profile
    profile = ProfileService.get_profile(db, user.id)

    return SigninResponse(
        user=UserResponse.model_validate(user),
        profile=ProfileResponse.model_validate(profile) if profile else None,
        token=token
    )


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sign out the current user (invalidate session).

    Requires authentication.
    """
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Requires authentication.
    """
    return UserResponse.model_validate(current_user)
