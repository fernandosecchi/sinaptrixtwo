"""Permission repository for permission-specific database operations."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.auth.permission import Permission
from src.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """Repository for Permission model operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize permission repository."""
        super().__init__(Permission, session)
    
    async def get_by_code(self, code: str) -> Optional[Permission]:
        """Get permission by its unique code."""
        query = select(Permission).where(Permission.code == code)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
        
    async def get_all_grouped_by_resource(self) -> List[Permission]:
        """Get all permissions ordered by resource."""
        query = select(Permission).order_by(Permission.resource, Permission.code)
        result = await self.session.execute(query)
        return list(result.scalars().all())
