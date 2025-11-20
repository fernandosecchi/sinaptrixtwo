"""Location service for geographic business logic."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.locations.country_repository import CountryRepository
from src.repositories.locations.state_repository import StateRepository
from src.repositories.locations.city_repository import CityRepository
from src.models.locations.country import Country
from src.models.locations.state import State
from src.models.locations.city import City


class LocationService:
    """Service for location-related business logic."""

    def __init__(self, session: AsyncSession):
        """
        Initialize location service.

        Args:
            session: Database session
        """
        self.session = session
        self.country_repository = CountryRepository(session)
        self.state_repository = StateRepository(session)
        self.city_repository = CityRepository(session)

    # Country methods
    async def get_all_countries(self) -> List[Dict[str, Any]]:
        """
        Get all active countries.

        Returns:
            List of country dictionaries
        """
        countries = await self.country_repository.get_active_countries()
        return [country.to_dict() for country in countries]

    async def get_countries_by_region(self, subregion: str) -> List[Dict[str, Any]]:
        """
        Get countries filtered by subregion.

        Args:
            subregion: Subregion name (North America, South America, Central America, Caribbean)

        Returns:
            List of country dictionaries
        """
        countries = await self.country_repository.get_active_countries(subregion=subregion)
        return [country.to_dict() for country in countries]

    async def get_country_by_id(self, country_id: int) -> Optional[Country]:
        """
        Get country by ID.

        Args:
            country_id: Country ID

        Returns:
            Country object or None
        """
        return await self.country_repository.get(country_id)

    async def get_country_by_code(self, code: str) -> Optional[Country]:
        """
        Get country by ISO code.

        Args:
            code: ISO 3166-1 alpha-2 code

        Returns:
            Country object or None
        """
        return await self.country_repository.get_by_code(code)

    async def search_countries(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search countries by name.

        Args:
            search_term: Search term

        Returns:
            List of matching country dictionaries
        """
        countries = await self.country_repository.search_by_name(search_term)
        return [country.to_dict() for country in countries]

    # State methods
    async def get_states_by_country(
        self,
        country_id: int,
        include_cities_count: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all states for a country.

        Args:
            country_id: Country ID
            include_cities_count: Whether to include city count for each state

        Returns:
            List of state dictionaries
        """
        if include_cities_count:
            return await self.state_repository.get_states_with_cities_count(country_id)

        states = await self.state_repository.get_by_country(country_id)
        return [state.to_dict() for state in states]

    async def get_state_by_id(self, state_id: int) -> Optional[State]:
        """
        Get state by ID.

        Args:
            state_id: State ID

        Returns:
            State object or None
        """
        return await self.state_repository.get(state_id)

    async def get_state_by_code(self, country_id: int, state_code: str) -> Optional[State]:
        """
        Get state by country and code.

        Args:
            country_id: Country ID
            state_code: State code

        Returns:
            State object or None
        """
        return await self.state_repository.get_by_country_and_code(country_id, state_code)

    async def search_states(
        self,
        search_term: str,
        country_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search states by name.

        Args:
            search_term: Search term
            country_id: Optional country filter

        Returns:
            List of matching state dictionaries
        """
        states = await self.state_repository.search_by_name(search_term, country_id)
        return [state.to_dict() for state in states]

    # City methods
    async def get_cities_by_state(
        self,
        state_id: int,
        min_population: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all cities for a state.

        Args:
            state_id: State ID
            min_population: Minimum population filter

        Returns:
            List of city dictionaries
        """
        cities = await self.city_repository.get_by_state(
            state_id,
            min_population=min_population
        )
        return [city.to_dict() for city in cities]

    async def get_cities_by_country(
        self,
        country_id: int,
        min_population: Optional[int] = None,
        limit: Optional[int] = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all cities for a country.

        Args:
            country_id: Country ID
            min_population: Minimum population filter
            limit: Maximum number of cities to return

        Returns:
            List of city dictionaries
        """
        cities = await self.city_repository.get_by_country(
            country_id,
            min_population=min_population,
            limit=limit
        )
        return [city.to_dict() for city in cities]

    async def get_city_by_id(self, city_id: int) -> Optional[City]:
        """
        Get city by ID.

        Args:
            city_id: City ID

        Returns:
            City object or None
        """
        return await self.city_repository.get(city_id)

    async def search_cities(
        self,
        search_term: str,
        country_id: Optional[int] = None,
        state_id: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search cities by name.

        Args:
            search_term: Search term
            country_id: Optional country filter
            state_id: Optional state filter
            limit: Maximum number of results

        Returns:
            List of matching city dictionaries
        """
        cities = await self.city_repository.search_by_name(
            search_term,
            country_id=country_id,
            state_id=state_id,
            limit=limit
        )
        return [city.to_dict() for city in cities]

    async def get_capital_cities(
        self,
        country_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get capital cities.

        Args:
            country_id: Optional country filter

        Returns:
            List of capital city dictionaries
        """
        cities = await self.city_repository.get_capitals(country_id=country_id)
        return [city.to_dict() for city in cities]

    async def get_major_cities(
        self,
        country_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get major cities by population.

        Args:
            country_id: Optional country filter
            limit: Maximum number of cities

        Returns:
            List of major city dictionaries
        """
        cities = await self.city_repository.get_major_cities(
            country_id=country_id,
            limit=limit
        )
        return [city.to_dict() for city in cities]

    # Composite methods
    async def get_location_hierarchy(
        self,
        country_id: Optional[int] = None,
        state_id: Optional[int] = None,
        city_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get complete location hierarchy based on provided IDs.

        Args:
            country_id: Country ID
            state_id: State ID
            city_id: City ID

        Returns:
            Dictionary with country, state, and city information
        """
        result = {
            "country": None,
            "state": None,
            "city": None
        }

        if city_id:
            city = await self.city_repository.get(city_id)
            if city:
                result["city"] = city.to_dict()
                state_id = city.state_id
                country_id = city.country_id

        if state_id:
            state = await self.state_repository.get(state_id)
            if state:
                result["state"] = state.to_dict()
                country_id = state.country_id

        if country_id:
            country = await self.country_repository.get(country_id)
            if country:
                result["country"] = country.to_dict()

        return result

    async def validate_location_ids(
        self,
        country_id: Optional[int] = None,
        state_id: Optional[int] = None,
        city_id: Optional[int] = None
    ) -> Dict[str, bool]:
        """
        Validate that location IDs exist and are consistent.

        Args:
            country_id: Country ID to validate
            state_id: State ID to validate
            city_id: City ID to validate

        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "errors": []
        }

        # Validate city
        if city_id:
            city = await self.city_repository.get(city_id)
            if not city:
                validation["valid"] = False
                validation["errors"].append("City not found")
            elif state_id and city.state_id != state_id:
                validation["valid"] = False
                validation["errors"].append("City does not belong to the specified state")
            elif country_id and city.country_id != country_id:
                validation["valid"] = False
                validation["errors"].append("City does not belong to the specified country")

        # Validate state
        if state_id:
            state = await self.state_repository.get(state_id)
            if not state:
                validation["valid"] = False
                validation["errors"].append("State not found")
            elif country_id and state.country_id != country_id:
                validation["valid"] = False
                validation["errors"].append("State does not belong to the specified country")

        # Validate country
        if country_id:
            country = await self.country_repository.get(country_id)
            if not country:
                validation["valid"] = False
                validation["errors"].append("Country not found")

        return validation