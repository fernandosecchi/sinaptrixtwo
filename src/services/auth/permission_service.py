"""Permission service for managing system permissions."""
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.auth.permission import Permission
from src.repositories.auth.permission_repository import PermissionRepository


class PermissionService:
    """Service layer for permission management."""

    def __init__(self, session: AsyncSession):
        """Initialize permission service."""
        self.repository = PermissionRepository(session)
        self.session = session

    async def get_permission(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID."""
        return await self.repository.get(permission_id)

    async def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """Get permission by unique code."""
        stmt = select(Permission).where(Permission.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions."""
        return await self.repository.get_all(order_by=Permission.resource)

    async def get_permissions_by_resource(self, resource: str) -> List[Permission]:
        """Get all permissions for a specific resource."""
        stmt = select(Permission).where(
            Permission.resource == resource
        ).order_by(Permission.action)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_permissions_grouped(self) -> Dict[str, List[Permission]]:
        """Get all permissions grouped by resource."""
        permissions = await self.get_all_permissions()
        grouped = {}
        for perm in permissions:
            if perm.resource not in grouped:
                grouped[perm.resource] = []
            grouped[perm.resource].append(perm)
        return grouped

    async def create_permission(
        self,
        code: str,
        name: str,
        resource: str,
        action: str,
        description: Optional[str] = None
    ) -> Permission:
        """Create a new permission."""
        # Check if code already exists
        existing = await self.get_permission_by_code(code)
        if existing:
            raise ValueError(f"El permiso con código '{code}' ya existe")

        # Validate format
        if not code or ':' not in code:
            raise ValueError("El código debe tener formato 'recurso:acción'")

        # Create permission
        return await self.repository.create(
            code=code,
            name=name,
            resource=resource,
            action=action,
            description=description
        )

    async def update_permission(
        self,
        permission_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Permission]:
        """Update permission details (name and description only)."""
        permission = await self.get_permission(permission_id)
        if not permission:
            return None

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description

        if update_data:
            return await self.repository.update(permission_id, **update_data)

        return permission

    async def delete_permission(self, permission_id: int) -> bool:
        """Delete a permission (will remove it from all roles)."""
        permission = await self.get_permission(permission_id)
        if not permission:
            return False

        # Check if it's a system permission (basic ones)
        system_codes = [
            'dashboard:view',
            'user:read', 'user:create', 'user:update', 'user:delete',
            'role:read', 'role:create', 'role:update', 'role:delete'
        ]

        if permission.code in system_codes:
            raise ValueError(f"No se puede eliminar el permiso del sistema '{permission.code}'")

        return await self.repository.delete(permission_id)

    async def get_available_resources(self) -> List[str]:
        """Get list of unique resources."""
        stmt = select(Permission.resource).distinct()
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_available_actions(self) -> List[str]:
        """Get list of unique actions."""
        stmt = select(Permission.action).distinct()
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def bulk_create_permissions(self, permissions_data: List[Dict]) -> List[Permission]:
        """Create multiple permissions at once."""
        created = []
        for perm_data in permissions_data:
            try:
                perm = await self.create_permission(**perm_data)
                created.append(perm)
            except ValueError as e:
                # Skip if already exists
                continue
        return created