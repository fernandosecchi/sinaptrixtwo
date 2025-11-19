"""Base repository with common CRUD operations."""
from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations."""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """Initialize repository with model and session."""
        self.model = model
        self.session = session
    
    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        return await self.session.get(self.model, id)
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[Any] = None
    ) -> List[ModelType]:
        """Get all records with optional pagination."""
        query = select(self.model)
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update a record by ID."""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def count(self) -> int:
        """Count total records."""
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def exists(self, **kwargs) -> bool:
        """Check if a record exists with given criteria."""
        query = select(self.model)
        for key, value in kwargs.items():
            query = query.where(getattr(self.model, key) == value)
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.scalar() is not None
    
    async def filter(self, **kwargs) -> List[ModelType]:
        """Filter records by given criteria."""
        query = select(self.model)
        for key, value in kwargs.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return list(result.scalars().all())