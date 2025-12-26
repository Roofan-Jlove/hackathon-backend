from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Tuple, Optional
from uuid import UUID

from app.models import User, Session as SessionModel
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import ACCESS_TOKEN_EXPIRE_DAYS


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def signup(db: Session, email: str, password: str) -> Tuple[User, str]:
        """
        Create a new user account.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            Tuple of (User, access_token)

        Raises:
            HTTPException: If email already exists
        """
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        hashed_password = hash_password(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Create session and token
        token = AuthService._create_session(db, user)

        return user, token

    @staticmethod
    def signin(db: Session, email: str, password: str) -> Tuple[User, str]:
        """
        Sign in an existing user.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            Tuple of (User, access_token)

        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Create session and token
        token = AuthService._create_session(db, user)

        return user, token

    @staticmethod
    def signout(db: Session, token: str) -> None:
        """
        Sign out a user by invalidating their session.

        Args:
            db: Database session
            token: JWT token
        """
        session = db.query(SessionModel).filter(SessionModel.token == token).first()
        if session:
            db.delete(session)
            db.commit()

    @staticmethod
    def _create_session(db: Session, user: User, ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None) -> str:
        """
        Create a new session for a user.

        Args:
            db: Database session
            user: User object
            ip_address: Optional IP address
            user_agent: Optional user agent string

        Returns:
            JWT access token
        """
        # Create token
        token_data = {"sub": str(user.id)}
        expires_delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        token = create_access_token(token_data, expires_delta)

        # Create session record
        expires_at = datetime.utcnow() + expires_delta
        session = SessionModel(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(session)
        db.commit()

        return token
