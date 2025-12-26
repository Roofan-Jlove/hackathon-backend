from typing import Dict, Optional
from uuid import UUID, uuid4
from datetime import datetime

# Placeholder for database interaction
# In a real app, this would use an ORM like SQLAlchemy or directly psycopg2
# and connect to Neon Postgres.

class UserProfile:
    def __init__(self, id: UUID, email: str, created_at: datetime,
                 software_background: Optional[Dict[str, str]] = None,
                 hardware_background: Optional[Dict[str, str]] = None):
        self.id = id
        self.email = email
        self.created_at = created_at
        self.software_background = software_background if software_background is not None else {}
        self.hardware_background = hardware_background if hardware_background is not None else {}

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "software_background": self.software_background,
            "hardware_background": self.hardware_background,
        }

# In-memory mock database for demonstration
_mock_db_users: Dict[UUID, UserProfile] = {}

async def create_user_profile(user_id: UUID, email: str, software_background: Dict[str, str], hardware_background: Dict[str, str]) -> UserProfile:
    """
    Creates a new user profile in the database.
    """
    if user_id in _mock_db_users:
        raise ValueError(f"User with ID {user_id} already exists.")
    
    new_profile = UserProfile(
        id=user_id,
        email=email,
        created_at=datetime.now(),
        software_background=software_background,
        hardware_background=hardware_background
    )
    _mock_db_users[user_id] = new_profile
    return new_profile

async def get_user_profile(user_id: UUID) -> Optional[UserProfile]:
    """
    Retrieves a user profile by ID from the database.
    """
    return _mock_db_users.get(user_id)

async def update_user_profile(user_id: UUID, software_background: Optional[Dict[str, str]] = None, hardware_background: Optional[Dict[str, str]] = None) -> Optional[UserProfile]:
    """
    Updates an existing user profile.
    """
    profile = _mock_db_users.get(user_id)
    if profile:
        if software_background is not None:
            profile.software_background = software_background
        if hardware_background is not None:
            profile.hardware_background = hardware_background
    return profile
