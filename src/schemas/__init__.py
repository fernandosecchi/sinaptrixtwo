"""Schemas package for data validation and serialization."""
from src.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserList
)
from src.schemas.lead import (
    LeadBase,
    LeadCreate,
    LeadUpdate,
    LeadStatusUpdate,
    LeadInDB,
    LeadResponse,
    LeadStatistics,
    LeadList
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate", 
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserList",
    # Lead schemas
    "LeadBase",
    "LeadCreate",
    "LeadUpdate",
    "LeadStatusUpdate",
    "LeadInDB",
    "LeadResponse",
    "LeadStatistics",
    "LeadList",
]