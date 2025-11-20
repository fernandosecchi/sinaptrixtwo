"""Authentication service with JWT support."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import secrets
import uuid

from src.models.auth import User, RefreshToken
from src.schemas.auth import TokenData, UserCreate
from src.config.settings import settings
from src.services.auth.password_service import PasswordService


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.password_service = PasswordService()
        self.algorithm = "HS256"
        self.access_token_expire_minutes = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 30)
        self.refresh_token_expire_days = getattr(settings, 'REFRESH_TOKEN_EXPIRE_DAYS', 7)
        self.secret_key = getattr(settings, 'SECRET_KEY', self._generate_secret_key())

    @staticmethod
    def _generate_secret_key() -> str:
        """Generate a secure secret key if not provided."""
        return secrets.token_urlsafe(32)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return self.password_service.verify_password(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return self.password_service.hash_password(password)

    async def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username or email and password.

        Args:
            username_or_email: Username or email address
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        # Query user by username or email
        stmt = select(User).where(
            (User.username == username_or_email) |
            (User.email == username_or_email)
        ).options(selectinload(User.roles))

        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Check if account is locked
        if user.is_locked:
            return None

        # Verify password
        if not self.verify_password(password, user.hashed_password):
            # Increment failed login attempts
            user.failed_login_attempts += 1

            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)

            await self.session.commit()
            return None

        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        await self.session.commit()

        return user

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.

        Args:
            data: Token payload data
            expires_delta: Optional expiration time delta

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return encoded_jwt

    async def create_refresh_token(self, user: User, user_agent: str = None, ip_address: str = None) -> str:
        """
        Create and store a refresh token.

        Args:
            user: User object
            user_agent: Client user agent string
            ip_address: Client IP address

        Returns:
            Encoded refresh token
        """
        # Generate unique JWT ID
        jti = str(uuid.uuid4())

        # Create token data
        expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "jti": jti,
            "exp": expires_at,
            "type": "refresh"
        }

        # Encode token
        refresh_token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)

        # Store in database
        db_token = RefreshToken(
            token=refresh_token,
            jti=jti,
            user_id=user.id,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at
        )

        self.session.add(db_token)
        await self.session.commit()

        return refresh_token

    async def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenData]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token to verify
            token_type: Expected token type ("access" or "refresh")

        Returns:
            TokenData if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != token_type:
                return None

            # For refresh tokens, check if revoked
            if token_type == "refresh":
                jti = payload.get("jti")
                if jti:
                    stmt = select(RefreshToken).where(
                        RefreshToken.jti == jti,
                        RefreshToken.is_active == True
                    )
                    result = await self.session.execute(stmt)
                    db_token = result.scalar_one_or_none()

                    if not db_token or not db_token.is_valid:
                        return None

                    # Update last used
                    db_token.update_last_used()
                    await self.session.commit()

            # Get user with roles
            user_id = payload.get("user_id")
            if user_id:
                stmt = select(User).where(User.id == user_id).options(selectinload(User.roles))
                result = await self.session.execute(stmt)
                user = result.scalar_one_or_none()

                if user and user.is_active and not user.is_deleted:
                    return TokenData(
                        user_id=user.id,
                        username=user.username,
                        email=user.email,
                        is_superuser=user.is_superuser,
                        roles=[role.name for role in user.roles],
                        permissions=list(user.permissions),
                        jti=payload.get("jti")
                    )

            return None

        except JWTError:
            return None

    async def refresh_access_token(self, refresh_token: str) -> Optional[tuple[str, str]]:
        """
        Use a refresh token to get a new access token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Tuple of (new_access_token, same_refresh_token) if valid, None otherwise
        """
        token_data = await self.verify_token(refresh_token, token_type="refresh")

        if not token_data:
            return None

        # Get user
        stmt = select(User).where(User.id == token_data.user_id).options(selectinload(User.roles))
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        # Create new access token
        access_token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "roles": [role.name for role in user.roles]
        }

        new_access_token = self.create_access_token(access_token_data)

        return new_access_token, refresh_token

    async def revoke_refresh_token(self, token: str, reason: str = "User logout") -> bool:
        """
        Revoke a refresh token.

        Args:
            token: Refresh token to revoke
            reason: Reason for revocation

        Returns:
            True if revoked successfully, False otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")

            if jti:
                stmt = select(RefreshToken).where(RefreshToken.jti == jti)
                result = await self.session.execute(stmt)
                db_token = result.scalar_one_or_none()

                if db_token:
                    db_token.revoke(reason)
                    await self.session.commit()
                    return True

        except JWTError:
            pass

        return False

    async def revoke_all_user_tokens(self, user_id: int, reason: str = "Security reset") -> int:
        """
        Revoke all refresh tokens for a user.

        Args:
            user_id: User ID
            reason: Reason for revocation

        Returns:
            Number of tokens revoked
        """
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_active == True
        )
        result = await self.session.execute(stmt)
        tokens = result.scalars().all()

        count = 0
        for token in tokens:
            token.revoke(reason)
            count += 1

        if count > 0:
            await self.session.commit()

        return count

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with hashed password.

        Args:
            user_data: User creation data

        Returns:
            Created user object
        """
        # Check if user exists
        stmt = select(User).where(
            (User.username == user_data.username) |
            (User.email == user_data.email)
        )
        result = await self.session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("Username or email already registered")

        # Create user with hashed password
        hashed_password = self.get_password_hash(user_data.password)

        db_user = User(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            is_verified=user_data.is_verified
        )

        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)

        return db_user

    async def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """
        Change user password.

        Args:
            user: User object
            current_password: Current password
            new_password: New password

        Returns:
            True if successful, False otherwise
        """
        # Verify current password
        if not self.verify_password(current_password, user.hashed_password):
            return False

        # Update password
        user.hashed_password = self.get_password_hash(new_password)
        user.password_changed_at = datetime.utcnow()

        # Revoke all refresh tokens for security
        await self.revoke_all_user_tokens(user.id, "Password changed")

        await self.session.commit()
        return True