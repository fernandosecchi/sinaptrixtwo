"""Permission model for granular access control."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


class Permission(Base):
    """Permission model for fine-grained access control."""
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Permission identification
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Categorization
    resource: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g., 'user', 'lead', 'dashboard'
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'create', 'read', 'update', 'delete'

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="select"
    )

    @classmethod
    def create_code(cls, resource: str, action: str) -> str:
        """Generate a permission code from resource and action."""
        return f"{resource}:{action}"

    def __repr__(self):
        return f"<Permission(id={self.id}, code='{self.code}', name='{self.name}')>"