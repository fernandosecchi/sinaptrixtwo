"""User schemas for data validation and serialization."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., max_length=255)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=255)


class UserInDB(UserBase):
    """Schema for user in database."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """Schema for user response."""
    full_name: str
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class UserList(BaseModel):
    """Schema for list of users response."""
    users: list[UserResponse]
    total: int
    page: int = 1
    page_size: int = 10