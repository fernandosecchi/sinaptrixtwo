"""Role model for RBAC (Role-Based Access Control)."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Boolean, Text, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


# Association table for role-permission relationship
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)


class Role(Base):
    """Role model for grouping permissions."""
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=None,
        onupdate=datetime.utcnow,
        nullable=True
    )

    # Relationships
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="select"
    )

    def add_permission(self, permission: "Permission") -> None:
        """Add a permission to this role."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: "Permission") -> None:
        """Remove a permission from this role."""
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission_code: str) -> bool:
        """Check if this role has a specific permission."""
        return any(p.code == permission_code for p in self.permissions)

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', permissions={len(self.permissions)})>"