# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

SinaptrixTwo is a unified FastAPI + NiceGUI application that integrates a reactive Python-based UI directly with a REST API backend, using PostgreSQL for persistence. The stack leverages modern async patterns throughout.

## Architecture

### Core Components

**src/main.py**
- Entry point that initializes both FastAPI and NiceGUI
- NiceGUI is mounted directly on FastAPI using `ui.run_with(app, ...)` 
- Defines UI layout with `theme_layout` context manager for consistent page structure
- Pages are defined with `@ui.page("/")` decorators
- Includes health check endpoint at `/health`

**src/database.py**
- Async SQLAlchemy configuration using `asyncpg` driver
- Provides `AsyncSessionLocal` factory and `get_db` dependency
- Base class for all models: `Base(DeclarativeBase)`
- Connection string from `DATABASE_URL` environment variable

### Infrastructure

- **Docker Compose**: Orchestrates app container and PostgreSQL database
- **PostgreSQL 15**: Database with health checks configured
- **Alembic**: Database migrations (async-compatible)
- **Poetry**: Python dependency management

## Development Commands

### Running the Application

Docker (preferred):
```bash
./scripts/start-docker.sh
# or directly:
docker-compose up --build
```

Local development (requires PostgreSQL):
```bash
poetry install
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Database Migrations

Create new migration:
```bash
docker-compose exec app poetry run alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
docker-compose exec app poetry run alembic upgrade head
```

### Environment Setup

```bash
cp .env.example .env
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string with asyncpg driver
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Database credentials
- `APP_ENV`: Set to "development" for SQL query logging

## Code Patterns

### NiceGUI Page Structure
Pages use the `theme_layout` context manager for consistent UI:
```python
@ui.page("/path")
def page_function():
    with theme_layout('Page Title'):
        # Page content here
```

### Database Sessions
Use async context manager pattern:
```python
async with AsyncSessionLocal() as session:
    # Database operations
```

### UI Components
- Interactive elements bind directly to Python variables/functions
- Use `.classes()` for Tailwind CSS styling
- Dark mode toggle built into header
- Responsive drawer navigation

## Endpoints

- Application: http://localhost:8000
- Health Check: http://localhost:8000/health
- Database: localhost:5432 (PostgreSQL)

## Notes

- No test suite currently configured
- No linting/formatting tools configured yet
- NiceGUI storage secret should be changed for production
- Application auto-reloads in development mode