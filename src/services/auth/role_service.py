"""Role service for role management logic."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.auth.role import Role
from src.repositories.auth.role_repository import RoleRepository
from src.repositories.auth.permission_repository import PermissionRepository
from src.schemas.auth.role import RoleCreate, RoleUpdate


class RoleService:
    """Service layer for role and permission management."""
    
    def __init__(self, session: AsyncSession):
        """Initialize role service."""
        self.role_repository = RoleRepository(session)
        self.permission_repository = PermissionRepository(session)
    
    async def get_role(self, role_id: int) -> Optional[Role]:
        """Get role by ID."""
        return await self.role_repository.get(role_id)
    
    async def get_all_roles(self) -> List[Role]:
        """Get all roles."""
        return await self.role_repository.get_all(order_by=Role.name)
    
    async def create_role(self, role_in: RoleCreate) -> Role:
        """Create a new role with optional permissions."""
        # Check if role name exists
        existing_role = await self.role_repository.get_by_name(role_in.name)
        if existing_role:
            raise ValueError(f"El rol '{role_in.name}' ya existe")
            
        # Create basic role
        role_data = role_in.model_dump(exclude={"permission_ids"})
        role = await self.role_repository.create(**role_data)
        
        # Add permissions if provided
        if role_in.permission_ids:
            await self._update_role_permissions(role, role_in.permission_ids)
            # Refresh to get relationships loaded
            await self.role_repository.session.refresh(role)
            
        return role
    
    async def update_role(self, role_id: int, role_in: RoleUpdate) -> Optional[Role]:
        """Update a role and its permissions."""
        role = await self.get_role(role_id)
        if not role:
            return None
            
        # Check name uniqueness if changing name
        if role_in.name and role_in.name != role.name:
            existing_role = await self.role_repository.get_by_name(role_in.name)
            if existing_role:
                raise ValueError(f"El rol '{role_in.name}' ya existe")
        
        # Update basic fields
        update_data = role_in.model_dump(exclude={"permission_ids"}, exclude_unset=True)
        if update_data:
            await self.role_repository.update(role_id, **update_data)
            # Refresh role instance
            await self.role_repository.session.refresh(role)
            
        # Update permissions if provided
        if role_in.permission_ids is not None:
            await self._update_role_permissions(role, role_in.permission_ids)
            await self.role_repository.session.refresh(role)
            
        return role
        
    async def delete_role(self, role_id: int) -> bool:
        """Delete a role."""
        # Get the role first to check if it's a system role
        role = await self.get_role(role_id)
        if not role:
            return False

        # Define system roles that cannot be deleted
        SYSTEM_ROLES = ['Administrador', 'Manager', 'Vendedor', 'Viewer']

        if role.name in SYSTEM_ROLES:
            raise ValueError(f"No se puede eliminar el rol del sistema '{role.name}'")

        return await self.role_repository.delete(role_id)
        
    async def _update_role_permissions(self, role: Role, permission_ids: List[int]) -> None:
        """Helper to update permissions for a role."""
        # Clear existing permissions
        role.permissions.clear()
        
        # Add new permissions
        for perm_id in permission_ids:
            permission = await self.permission_repository.get(perm_id)
            if permission:
                role.permissions.append(permission)
                
        await self.role_repository.session.commit()

    async def get_all_permissions(self) -> List:
        """Get all available permissions."""
        return await self.permission_repository.get_all_grouped_by_resource()
