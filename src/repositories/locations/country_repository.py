"""Country repository for data access."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.locations.country import Country
from src.repositories.base import BaseRepository


class CountryRepository(BaseRepository[Country]):
    """Repository for Country model."""

    def __init__(self, session: AsyncSession):
        """Initialize country repository."""
        super().__init__(Country, session)

    async def get_active_countries(
        self,
        subregion: Optional[str] = None
    ) -> List[Country]:
        """
        Get all active countries, optionally filtered by subregion.

        Args:
            subregion: Optional subregion filter (North America, South America, etc.)

        Returns:
            List of active countries
        """
        query = select(self.model).where(self.model.is_active == True)

        if subregion:
            query = query.where(self.model.subregion == subregion)

        query = query.order_by(self.model.name)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_code(self, code: str) -> Optional[Country]:
        """
        Get country by 2-letter code.

        Args:
            code: ISO 3166-1 alpha-2 code

        Returns:
            Country if found, None otherwise
        """
        query = select(self.model).where(
            and_(
                self.model.code == code.upper(),
                self.model.is_active == True
            )
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code3(self, code3: str) -> Optional[Country]:
        """
        Get country by 3-letter code.

        Args:
            code3: ISO 3166-1 alpha-3 code

        Returns:
            Country if found, None otherwise
        """
        query = select(self.model).where(
            and_(
                self.model.code3 == code3.upper(),
                self.model.is_active == True
            )
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def search_by_name(self, search_term: str) -> List[Country]:
        """
        Search countries by name (supports multiple languages).

        Args:
            search_term: Search term to match against names

        Returns:
            List of matching countries
        """
        pattern = f"%{search_term}%"
        query = select(self.model).where(
            and_(
                self.model.is_active == True,
                (
                    self.model.name.ilike(pattern) |
                    self.model.name_es.ilike(pattern) |
                    self.model.name_pt.ilike(pattern) |
                    self.model.name_fr.ilike(pattern)
                )
            )
        ).order_by(self.model.name)

        result = await self._session.execute(query)
        return result.scalars().all()