"""Token schemas for JWT authentication."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: int
    username: str
    email: str
    is_superuser: bool = False
    roles: List[str] = []
    permissions: List[str] = []
    exp: Optional[datetime] = None
    jti: Optional[str] = None  # JWT ID for refresh tokens


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str  # Can be username or email
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Detailed token response with user info."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires
    user: dict  # Basic user information