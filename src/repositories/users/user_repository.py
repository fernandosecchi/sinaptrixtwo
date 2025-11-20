"""User repository for user-specific database operations."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.auth.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize user repository."""
        super().__init__(User, session)
    
    async def get_by_email(self, email: str, include_deleted: bool = False) -> Optional[User]:
        """Get user by email address."""
        query = select(User).where(User.email == email)
        if not include_deleted:
            query = query.where(User.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_active(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active (non-deleted) users."""
        query = (
            select(User)
            .where(User.is_deleted == False)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_all_deleted(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all soft-deleted users."""
        query = (
            select(User)
            .where(User.is_deleted == True)
            .order_by(User.deleted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def search(self, term: str, include_deleted: bool = False) -> List[User]:
        """Search users by name or email."""
        search_term = f"%{term}%"
        query = select(User).where(
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term)) |
            (User.email.ilike(search_term))
        )
        if not include_deleted:
            query = query.where(User.is_deleted == False)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def soft_delete(self, user_id: int) -> bool:
        """Soft delete a user (mark as deleted without removing from DB)."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .where(User.is_deleted == False)
            .values(
                is_deleted=True,
                deleted_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def restore(self, user_id: int) -> bool:
        """Restore a soft-deleted user."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .where(User.is_deleted == True)
            .values(
                is_deleted=False,
                deleted_at=None,
                updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def hard_delete(self, user_id: int) -> bool:
        """Permanently delete a user from database."""
        return await self.delete(user_id)
    
    async def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email already exists among active users."""
        query = select(User).where(User.email == email).where(User.is_deleted == False)
        if exclude_id:
            query = query.where(User.id != exclude_id)
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.scalar() is not None
