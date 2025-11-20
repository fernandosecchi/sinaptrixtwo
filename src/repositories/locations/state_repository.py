"""State/Province repository for data access."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.locations.state import State
from src.repositories.base import BaseRepository


class StateRepository(BaseRepository[State]):
    """Repository for State model."""

    def __init__(self, session: AsyncSession):
        """Initialize state repository."""
        super().__init__(State, session)

    async def get_by_country(
        self,
        country_id: int,
        include_country: bool = False
    ) -> List[State]:
        """
        Get all states for a specific country.

        Args:
            country_id: Country ID to filter by
            include_country: Whether to include country relationship

        Returns:
            List of states for the country
        """
        query = select(self.model).where(
            and_(
                self.model.country_id == country_id,
                self.model.is_active == True
            )
        ).order_by(self.model.name)

        if include_country:
            query = query.options(selectinload(self.model.country))

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_country_and_code(
        self,
        country_id: int,
        code: str
    ) -> Optional[State]:
        """
        Get state by country ID and state code.

        Args:
            country_id: Country ID
            code: State/Province code

        Returns:
            State if found, None otherwise
        """
        query = select(self.model).where(
            and_(
                self.model.country_id == country_id,
                self.model.code == code.upper(),
                self.model.is_active == True
            )
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def search_by_name(
        self,
        search_term: str,
        country_id: Optional[int] = None
    ) -> List[State]:
        """
        Search states by name, optionally filtered by country.

        Args:
            search_term: Search term to match against names
            country_id: Optional country ID filter

        Returns:
            List of matching states
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

        query = select(self.model).where(
            and_(*conditions)
        ).order_by(self.model.name)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_states_with_cities_count(
        self,
        country_id: int
    ) -> List[dict]:
        """
        Get states with count of cities for a country.

        Args:
            country_id: Country ID

        Returns:
            List of states with city counts
        """
        from sqlalchemy import func
        from src.models.locations.city import City

        query = (
            select(
                self.model,
                func.count(City.id).label('cities_count')
            )
            .outerjoin(City, and_(
                City.state_id == self.model.id,
                City.is_active == True
            ))
            .where(
                and_(
                    self.model.country_id == country_id,
                    self.model.is_active == True
                )
            )
            .group_by(self.model.id)
            .order_by(self.model.name)
        )

        result = await self._session.execute(query)
        states_with_counts = []

        for state, cities_count in result:
            state_dict = state.to_dict()
            state_dict['cities_count'] = cities_count
            states_with_counts.append(state_dict)

        return states_with_counts