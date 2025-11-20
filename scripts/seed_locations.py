#!/usr/bin/env python3
"""
Script to seed location data (countries, states, cities) for the American continent.
Run with: docker-compose exec app python scripts/seed_locations.py
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.locations.country import Country
from src.models.locations.state import State
from src.models.locations.city import City


async def seed_countries(session):
    """Seed countries data for American continent."""

    # Check if countries already exist
    result = await session.execute(select(Country).limit(1))
    if result.scalar_one_or_none():
        print("Countries already seeded, skipping...")
        return

    countries_data = [
        # North America
        {"code": "US", "code3": "USA", "name": "United States", "name_es": "Estados Unidos",
         "phone_prefix": "+1", "currency_code": "USD", "subregion": "North America",
         "capital": "Washington D.C.", "latitude": 37.0902, "longitude": -95.7129},

        {"code": "CA", "code3": "CAN", "name": "Canada", "name_es": "Canadá",
         "phone_prefix": "+1", "currency_code": "CAD", "subregion": "North America",
         "capital": "Ottawa", "latitude": 56.1304, "longitude": -106.3468},

        {"code": "MX", "code3": "MEX", "name": "Mexico", "name_es": "México",
         "phone_prefix": "+52", "currency_code": "MXN", "subregion": "North America",
         "capital": "Mexico City", "latitude": 23.6345, "longitude": -102.5528},

        # Central America
        {"code": "GT", "code3": "GTM", "name": "Guatemala", "name_es": "Guatemala",
         "phone_prefix": "+502", "currency_code": "GTQ", "subregion": "Central America",
         "capital": "Guatemala City", "latitude": 15.7835, "longitude": -90.2308},

        {"code": "HN", "code3": "HND", "name": "Honduras", "name_es": "Honduras",
         "phone_prefix": "+504", "currency_code": "HNL", "subregion": "Central America",
         "capital": "Tegucigalpa", "latitude": 15.2000, "longitude": -86.2419},

        {"code": "SV", "code3": "SLV", "name": "El Salvador", "name_es": "El Salvador",
         "phone_prefix": "+503", "currency_code": "USD", "subregion": "Central America",
         "capital": "San Salvador", "latitude": 13.7942, "longitude": -88.8965},

        {"code": "NI", "code3": "NIC", "name": "Nicaragua", "name_es": "Nicaragua",
         "phone_prefix": "+505", "currency_code": "NIO", "subregion": "Central America",
         "capital": "Managua", "latitude": 12.8654, "longitude": -85.2072},

        {"code": "CR", "code3": "CRI", "name": "Costa Rica", "name_es": "Costa Rica",
         "phone_prefix": "+506", "currency_code": "CRC", "subregion": "Central America",
         "capital": "San José", "latitude": 9.7489, "longitude": -83.7534},

        {"code": "PA", "code3": "PAN", "name": "Panama", "name_es": "Panamá",
         "phone_prefix": "+507", "currency_code": "PAB", "subregion": "Central America",
         "capital": "Panama City", "latitude": 8.5380, "longitude": -80.7821},

        # Caribbean
        {"code": "CU", "code3": "CUB", "name": "Cuba", "name_es": "Cuba",
         "phone_prefix": "+53", "currency_code": "CUP", "subregion": "Caribbean",
         "capital": "Havana", "latitude": 21.5218, "longitude": -77.7812},

        {"code": "DO", "code3": "DOM", "name": "Dominican Republic", "name_es": "República Dominicana",
         "phone_prefix": "+1809", "currency_code": "DOP", "subregion": "Caribbean",
         "capital": "Santo Domingo", "latitude": 18.7357, "longitude": -70.1627},

        # South America
        {"code": "CO", "code3": "COL", "name": "Colombia", "name_es": "Colombia",
         "phone_prefix": "+57", "currency_code": "COP", "subregion": "South America",
         "capital": "Bogotá", "latitude": 4.5709, "longitude": -74.2973},

        {"code": "VE", "code3": "VEN", "name": "Venezuela", "name_es": "Venezuela",
         "phone_prefix": "+58", "currency_code": "VES", "subregion": "South America",
         "capital": "Caracas", "latitude": 6.4238, "longitude": -66.5897},

        {"code": "EC", "code3": "ECU", "name": "Ecuador", "name_es": "Ecuador",
         "phone_prefix": "+593", "currency_code": "USD", "subregion": "South America",
         "capital": "Quito", "latitude": -1.8312, "longitude": -78.1834},

        {"code": "PE", "code3": "PER", "name": "Peru", "name_es": "Perú",
         "phone_prefix": "+51", "currency_code": "PEN", "subregion": "South America",
         "capital": "Lima", "latitude": -9.1900, "longitude": -75.0152},

        {"code": "BR", "code3": "BRA", "name": "Brazil", "name_es": "Brasil", "name_pt": "Brasil",
         "phone_prefix": "+55", "currency_code": "BRL", "subregion": "South America",
         "capital": "Brasília", "latitude": -14.2350, "longitude": -51.9253},

        {"code": "BO", "code3": "BOL", "name": "Bolivia", "name_es": "Bolivia",
         "phone_prefix": "+591", "currency_code": "BOB", "subregion": "South America",
         "capital": "La Paz", "latitude": -16.2902, "longitude": -63.5887},

        {"code": "PY", "code3": "PRY", "name": "Paraguay", "name_es": "Paraguay",
         "phone_prefix": "+595", "currency_code": "PYG", "subregion": "South America",
         "capital": "Asunción", "latitude": -23.4425, "longitude": -58.4438},

        {"code": "UY", "code3": "URY", "name": "Uruguay", "name_es": "Uruguay",
         "phone_prefix": "+598", "currency_code": "UYU", "subregion": "South America",
         "capital": "Montevideo", "latitude": -32.5228, "longitude": -55.7658},

        {"code": "AR", "code3": "ARG", "name": "Argentina", "name_es": "Argentina",
         "phone_prefix": "+54", "currency_code": "ARS", "subregion": "South America",
         "capital": "Buenos Aires", "latitude": -38.4161, "longitude": -63.6167},

        {"code": "CL", "code3": "CHL", "name": "Chile", "name_es": "Chile",
         "phone_prefix": "+56", "currency_code": "CLP", "subregion": "South America",
         "capital": "Santiago", "latitude": -35.6751, "longitude": -71.5430},
    ]

    for data in countries_data:
        country = Country(**data)
        session.add(country)

    await session.commit()
    print(f"✓ Loaded {len(countries_data)} countries")
    return countries_data


async def seed_states(session):
    """Seed major states/provinces for key countries."""

    # Check if states already exist
    result = await session.execute(select(State).limit(1))
    if result.scalar_one_or_none():
        print("States already seeded, skipping...")
        return

    # Get country references
    countries_result = await session.execute(select(Country))
    countries = {c.code: c for c in countries_result.scalars().all()}

    states_data = []

    # United States - Major states
    if "US" in countries:
        us_states = [
            {"code": "CA", "name": "California", "type": "state", "capital": "Sacramento"},
            {"code": "TX", "name": "Texas", "type": "state", "capital": "Austin"},
            {"code": "FL", "name": "Florida", "type": "state", "capital": "Tallahassee"},
            {"code": "NY", "name": "New York", "type": "state", "capital": "Albany"},
            {"code": "IL", "name": "Illinois", "type": "state", "capital": "Springfield"},
            {"code": "PA", "name": "Pennsylvania", "type": "state", "capital": "Harrisburg"},
            {"code": "OH", "name": "Ohio", "type": "state", "capital": "Columbus"},
            {"code": "GA", "name": "Georgia", "type": "state", "capital": "Atlanta"},
            {"code": "NC", "name": "North Carolina", "type": "state", "capital": "Raleigh"},
            {"code": "MI", "name": "Michigan", "type": "state", "capital": "Lansing"},
        ]
        for state_data in us_states:
            state_data["country_id"] = countries["US"].id
            states_data.append(state_data)

    # Canada - Major provinces
    if "CA" in countries:
        ca_provinces = [
            {"code": "ON", "name": "Ontario", "type": "province", "capital": "Toronto"},
            {"code": "QC", "name": "Quebec", "type": "province", "capital": "Quebec City"},
            {"code": "BC", "name": "British Columbia", "type": "province", "capital": "Victoria"},
            {"code": "AB", "name": "Alberta", "type": "province", "capital": "Edmonton"},
            {"code": "MB", "name": "Manitoba", "type": "province", "capital": "Winnipeg"},
        ]
        for state_data in ca_provinces:
            state_data["country_id"] = countries["CA"].id
            states_data.append(state_data)

    # Mexico - Major states
    if "MX" in countries:
        mx_states = [
            {"code": "CDMX", "name": "Ciudad de México", "type": "state", "capital": "Ciudad de México"},
            {"code": "JAL", "name": "Jalisco", "type": "state", "capital": "Guadalajara"},
            {"code": "NL", "name": "Nuevo León", "type": "state", "capital": "Monterrey"},
            {"code": "VER", "name": "Veracruz", "type": "state", "capital": "Xalapa"},
            {"code": "PUE", "name": "Puebla", "type": "state", "capital": "Puebla"},
        ]
        for state_data in mx_states:
            state_data["country_id"] = countries["MX"].id
            states_data.append(state_data)

    # Brazil - Major states
    if "BR" in countries:
        br_states = [
            {"code": "SP", "name": "São Paulo", "type": "state", "capital": "São Paulo"},
            {"code": "RJ", "name": "Rio de Janeiro", "type": "state", "capital": "Rio de Janeiro"},
            {"code": "MG", "name": "Minas Gerais", "type": "state", "capital": "Belo Horizonte"},
            {"code": "BA", "name": "Bahia", "type": "state", "capital": "Salvador"},
            {"code": "RS", "name": "Rio Grande do Sul", "type": "state", "capital": "Porto Alegre"},
            {"code": "PR", "name": "Paraná", "type": "state", "capital": "Curitiba"},
            {"code": "PE", "name": "Pernambuco", "type": "state", "capital": "Recife"},
            {"code": "CE", "name": "Ceará", "type": "state", "capital": "Fortaleza"},
        ]
        for state_data in br_states:
            state_data["country_id"] = countries["BR"].id
            states_data.append(state_data)

    # Argentina - Major provinces
    if "AR" in countries:
        ar_provinces = [
            {"code": "BA", "name": "Buenos Aires", "type": "province", "capital": "La Plata"},
            {"code": "CF", "name": "Ciudad Autónoma de Buenos Aires", "type": "district", "capital": "Buenos Aires"},
            {"code": "CO", "name": "Córdoba", "type": "province", "capital": "Córdoba"},
            {"code": "SF", "name": "Santa Fe", "type": "province", "capital": "Santa Fe"},
            {"code": "ME", "name": "Mendoza", "type": "province", "capital": "Mendoza"},
        ]
        for state_data in ar_provinces:
            state_data["country_id"] = countries["AR"].id
            states_data.append(state_data)

    # Create all states
    for data in states_data:
        state = State(**data)
        session.add(state)

    await session.commit()
    print(f"✓ Loaded {len(states_data)} states/provinces")
    return states_data


async def seed_cities(session):
    """Seed major cities."""

    # Check if cities already exist
    result = await session.execute(select(City).limit(1))
    if result.scalar_one_or_none():
        print("Cities already seeded, skipping...")
        return

    # Get country and state references
    countries_result = await session.execute(select(Country))
    countries = {c.code: c for c in countries_result.scalars().all()}

    states_result = await session.execute(select(State))
    states = {(s.country_id, s.code): s for s in states_result.scalars().all()}

    cities_data = []

    # United States - Major cities
    if "US" in countries:
        us_id = countries["US"].id
        us_cities = [
            {"state_code": "CA", "name": "Los Angeles", "population": 3990456, "latitude": 34.0522, "longitude": -118.2437},
            {"state_code": "CA", "name": "San Francisco", "population": 884363, "latitude": 37.7749, "longitude": -122.4194},
            {"state_code": "CA", "name": "San Diego", "population": 1425976, "latitude": 32.7157, "longitude": -117.1611},
            {"state_code": "TX", "name": "Houston", "population": 2325502, "latitude": 29.7604, "longitude": -95.3698},
            {"state_code": "TX", "name": "Dallas", "population": 1345047, "latitude": 32.7767, "longitude": -96.7970},
            {"state_code": "TX", "name": "Austin", "population": 964254, "latitude": 30.2672, "longitude": -97.7431, "is_capital": True},
            {"state_code": "FL", "name": "Miami", "population": 467963, "latitude": 25.7617, "longitude": -80.1918},
            {"state_code": "FL", "name": "Orlando", "population": 287442, "latitude": 28.5383, "longitude": -81.3792},
            {"state_code": "NY", "name": "New York City", "population": 8336817, "latitude": 40.7128, "longitude": -74.0060, "is_major_city": True},
            {"state_code": "IL", "name": "Chicago", "population": 2746388, "latitude": 41.8781, "longitude": -87.6298, "is_major_city": True},
        ]

        for city_data in us_cities:
            state_code = city_data.pop("state_code")
            if (us_id, state_code) in states:
                city_data["country_id"] = us_id
                city_data["state_id"] = states[(us_id, state_code)].id
                cities_data.append(city_data)

    # Canada - Major cities
    if "CA" in countries:
        ca_id = countries["CA"].id
        ca_cities = [
            {"state_code": "ON", "name": "Toronto", "population": 2731571, "latitude": 43.6532, "longitude": -79.3832, "is_major_city": True},
            {"state_code": "ON", "name": "Ottawa", "population": 934243, "latitude": 45.4215, "longitude": -75.6972, "is_national_capital": True},
            {"state_code": "QC", "name": "Montreal", "population": 1704694, "latitude": 45.5017, "longitude": -73.5673},
            {"state_code": "BC", "name": "Vancouver", "population": 631486, "latitude": 49.2827, "longitude": -123.1207},
            {"state_code": "AB", "name": "Calgary", "population": 1239220, "latitude": 51.0447, "longitude": -114.0719},
        ]

        for city_data in ca_cities:
            state_code = city_data.pop("state_code")
            if (ca_id, state_code) in states:
                city_data["country_id"] = ca_id
                city_data["state_id"] = states[(ca_id, state_code)].id
                cities_data.append(city_data)

    # Mexico - Major cities
    if "MX" in countries:
        mx_id = countries["MX"].id
        mx_cities = [
            {"state_code": "CDMX", "name": "Ciudad de México", "population": 8918653, "latitude": 19.4326, "longitude": -99.1332, "is_national_capital": True, "is_major_city": True},
            {"state_code": "JAL", "name": "Guadalajara", "population": 1495189, "latitude": 20.6597, "longitude": -103.3496},
            {"state_code": "NL", "name": "Monterrey", "population": 1135512, "latitude": 25.6866, "longitude": -100.3161},
            {"state_code": "PUE", "name": "Puebla", "population": 1434062, "latitude": 19.0414, "longitude": -98.2063},
        ]

        for city_data in mx_cities:
            state_code = city_data.pop("state_code")
            if (mx_id, state_code) in states:
                city_data["country_id"] = mx_id
                city_data["state_id"] = states[(mx_id, state_code)].id
                cities_data.append(city_data)

    # Brazil - Major cities
    if "BR" in countries:
        br_id = countries["BR"].id
        br_cities = [
            {"state_code": "SP", "name": "São Paulo", "population": 12325232, "latitude": -23.5505, "longitude": -46.6333, "is_major_city": True},
            {"state_code": "RJ", "name": "Rio de Janeiro", "population": 6747815, "latitude": -22.9068, "longitude": -43.1729, "is_major_city": True},
            {"state_code": "MG", "name": "Belo Horizonte", "population": 2521564, "latitude": -19.9167, "longitude": -43.9345},
            {"state_code": "BA", "name": "Salvador", "population": 2872347, "latitude": -12.9714, "longitude": -38.5014},
            {"state_code": "RS", "name": "Porto Alegre", "population": 1481019, "latitude": -30.0346, "longitude": -51.2177},
            {"state_code": "PR", "name": "Curitiba", "population": 1948626, "latitude": -25.4244, "longitude": -49.2654},
            {"state_code": "PE", "name": "Recife", "population": 1653461, "latitude": -8.0476, "longitude": -34.8770},
            {"state_code": "CE", "name": "Fortaleza", "population": 2686612, "latitude": -3.7319, "longitude": -38.5267},
        ]

        for city_data in br_cities:
            state_code = city_data.pop("state_code")
            if (br_id, state_code) in states:
                city_data["country_id"] = br_id
                city_data["state_id"] = states[(br_id, state_code)].id
                cities_data.append(city_data)

    # Argentina - Major cities
    if "AR" in countries:
        ar_id = countries["AR"].id
        ar_cities = [
            {"state_code": "CF", "name": "Buenos Aires", "population": 2890151, "latitude": -34.6037, "longitude": -58.3816, "is_national_capital": True, "is_major_city": True},
            {"state_code": "CO", "name": "Córdoba", "population": 1329604, "latitude": -31.4201, "longitude": -64.1888},
            {"state_code": "SF", "name": "Rosario", "population": 1193605, "latitude": -32.9442, "longitude": -60.6505},
            {"state_code": "ME", "name": "Mendoza", "population": 115041, "latitude": -32.8895, "longitude": -68.8458},
        ]

        for city_data in ar_cities:
            state_code = city_data.pop("state_code")
            if (ar_id, state_code) in states:
                city_data["country_id"] = ar_id
                city_data["state_id"] = states[(ar_id, state_code)].id
                cities_data.append(city_data)

    # Create all cities
    for data in cities_data:
        city = City(**data)
        session.add(city)

    await session.commit()
    print(f"✓ Loaded {len(cities_data)} cities")


async def main():
    """Main function to seed all location data."""
    print("Starting location data seeding...")

    async with AsyncSessionLocal() as session:
        try:
            # Seed in order: countries -> states -> cities
            await seed_countries(session)
            await seed_states(session)
            await seed_cities(session)

            print("\n✅ Location data seeding completed successfully!")

            # Show statistics
            from sqlalchemy import func
            countries_count = await session.execute(select(func.count(Country.id)))
            states_count = await session.execute(select(func.count(State.id)))
            cities_count = await session.execute(select(func.count(City.id)))

            print(f"\nStatistics:")
            print(f"  Countries: {countries_count.scalar()}")
            print(f"  States/Provinces: {states_count.scalar()}")
            print(f"  Cities: {cities_count.scalar()}")

        except Exception as e:
            print(f"\n❌ Error seeding location data: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())