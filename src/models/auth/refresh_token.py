"""Refresh token model for JWT authentication."""
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


class RefreshToken(Base):
    """Refresh token model for managing JWT refresh tokens."""
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Token information
    token: Mapped[str] = mapped_column(Text, unique=True, index=True, nullable=False)
    jti: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)  # JWT ID

    # User relationship
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Metadata
    user_agent: Mapped[str] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # Supports IPv6

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    revoked_reason: Mapped[str] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the token is valid (active and not expired)."""
        return self.is_active and not self.is_expired

    def revoke(self, reason: str = None) -> None:
        """Revoke this refresh token."""
        self.is_active = False
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason or "Manual revocation"

    def update_last_used(self) -> None:
        """Update the last used timestamp."""
        self.last_used_at = datetime.utcnow()

    def __repr__(self):
        status = "valid" if self.is_valid else "invalid"
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, status={status})>"