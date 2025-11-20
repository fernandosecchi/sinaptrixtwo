"""City repository for data access."""
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.locations.city import City
from src.repositories.base import BaseRepository


class CityRepository(BaseRepository[City]):
    """Repository for City model."""

    def __init__(self, session: AsyncSession):
        """Initialize city repository."""
        super().__init__(City, session)

    async def get_by_state(
        self,
        state_id: int,
        include_relationships: bool = False,
        min_population: Optional[int] = None
    ) -> List[City]:
        """
        Get all cities for a specific state.

        Args:
            state_id: State ID to filter by
            include_relationships: Whether to include state and country relationships
            min_population: Minimum population filter

        Returns:
            List of cities for the state
        """
        conditions = [
            self.model.state_id == state_id,
            self.model.is_active == True
        ]

        if min_population:
            conditions.append(self.model.population >= min_population)

        query = select(self.model).where(
            and_(*conditions)
        ).order_by(self.model.population.desc().nullslast(), self.model.name)

        if include_relationships:
            query = query.options(
                selectinload(self.model.state),
                selectinload(self.model.country)
            )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_country(
        self,
        country_id: int,
        include_relationships: bool = False,
        min_population: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[City]:
        """
        Get all cities for a specific country.

        Args:
            country_id: Country ID to filter by
            include_relationships: Whether to include state and country relationships
            min_population: Minimum population filter
            limit: Maximum number of cities to return

        Returns:
            List of cities for the country
        """
        conditions = [
            self.model.country_id == country_id,
            self.model.is_active == True
        ]

        if min_population:
            conditions.append(self.model.population >= min_population)

        query = select(self.model).where(
            and_(*conditions)
        ).order_by(self.model.population.desc().nullslast(), self.model.name)

        if include_relationships:
            query = query.options(
                selectinload(self.model.state),
                selectinload(self.model.country)
            )

        if limit:
            query = query.limit(limit)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def search_by_name(
        self,
        search_term: str,
        country_id: Optional[int] = None,
        state_id: Optional[int] = None,
        limit: int = 20
    ) -> List[City]:
        """
        Search cities by name, optionally filtered by country or state.

        Args:
            search_term: Search term to match against names
            country_id: Optional country ID filter
            state_id: Optional state ID filter
            limit: Maximum number of results

        Returns:
            List of matching cities
        """
        pattern = f"%{search_term}%"
        conditions = [
            self.model.is_active == True,
            (
                self.model.name.ilike(pattern) |
                self.model.name_ascii.ilike(pattern)
            )
        ]

        if country_id:
            conditions.append(self.model.country_id == country_id)

        if state_id:
            conditions.append(self.model.state_id == state_id)

        query = (
            select(self.model)
            .where(and_(*conditions))
            .order_by(self.model.population.desc().nullslast(), self.model.name)
            .limit(limit)
        )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_capitals(
        self,
        country_id: Optional[int] = None,
        include_national: bool = True,
        include_state: bool = True
    ) -> List[City]:
        """
        Get capital cities.

        Args:
            country_id: Optional country ID filter
            include_national: Include national capitals
            include_state: Include state capitals

        Returns:
            List of capital cities
        """
        conditions = [self.model.is_active == True]

        if country_id:
            conditions.append(self.model.country_id == country_id)

        capital_conditions = []
        if include_national:
            capital_conditions.append(self.model.is_national_capital == True)
        if include_state:
            capital_conditions.append(self.model.is_capital == True)

        if capital_conditions:
            conditions.append(or_(*capital_conditions))

        query = (
            select(self.model)
            .where(and_(*conditions))
            .options(
                selectinload(self.model.state),
                selectinload(self.model.country)
            )
            .order_by(
                self.model.is_national_capital.desc(),
                self.model.population.desc().nullslast(),
                self.model.name
            )
        )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_major_cities(
        self,
        country_id: Optional[int] = None,
        limit: int = 10
    ) -> List[City]:
        """
        Get major cities by population.

        Args:
            country_id: Optional country ID filter
            limit: Maximum number of cities to return

        Returns:
            List of major cities
        """
        conditions = [
            self.model.is_active == True,
            or_(
                self.model.is_major_city == True,
                self.model.population > 500000
            )
        ]

        if country_id:
            conditions.append(self.model.country_id == country_id)

        query = (
            select(self.model)
            .where(and_(*conditions))
            .options(
                selectinload(self.model.state),
                selectinload(self.model.country)
            )
            .order_by(self.model.population.desc().nullslast())
            .limit(limit)
        )

        result = await self._session.execute(query)
        return result.scalars().all()