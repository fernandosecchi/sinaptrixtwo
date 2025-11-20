"""Schemas package for data validation and serialization."""
from src.schemas.users.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserList
)
from src.schemas.leads.lead import (
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