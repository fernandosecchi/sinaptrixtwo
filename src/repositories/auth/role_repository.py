"""Role repository for role-specific database operations."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.auth.role import Role
from src.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for Role model operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize role repository."""
        super().__init__(Role, session)
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        query = select(Role).where(Role.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
