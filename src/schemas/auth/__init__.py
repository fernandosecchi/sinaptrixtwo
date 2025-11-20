"""Auth schemas package."""
from src.schemas.auth.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    UserInDB,
)
from src.schemas.auth.token import (
    Token,
    TokenData,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from src.schemas.auth.role import (
    PermissionBase,
    PermissionCreate,
    PermissionResponse,
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    UserRoleAssignment,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPasswordUpdate",
    "UserResponse",
    "UserInDB",
    # Token schemas
    "Token",
    "TokenData",
    "LoginRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    # Role and Permission schemas
    "PermissionBase",
    "PermissionCreate",
    "PermissionResponse",
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "UserRoleAssignment",
]