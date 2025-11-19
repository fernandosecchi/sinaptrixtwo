# SinaptrixTwo

A unified FastAPI + NiceGUI application with PostgreSQL, managed by Poetry and Docker.

## Tech Stack

- **Language:** Python 3.11
- **Web Framework:** FastAPI
- **Frontend Framework:** NiceGUI (Native integration with FastAPI)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy (Async)
- **Migrations:** Alembic
- **Dependency Management:** Poetry
- **Containerization:** Docker & Docker Compose

## Quick Start (Docker)

The easiest way to run the application is using Docker Compose.

1. Ensure Docker and Docker Compose are installed.
2. Create `.env` file from example:
   ```bash
   cp .env.example .env
   ```
3. Run the start script:
   ```bash
   ./scripts/start-docker.sh
   ```
   Or manually:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - **Frontend & API:** http://localhost:8000
   - **Health Check:** http://localhost:8000/health

## Development Setup (Local)

If you prefer to run locally without Docker for the app (you still need a DB):

1. Install Poetry (if not already installed).
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Ensure a PostgreSQL database is running and update `.env` with the correct `DATABASE_URL`.
4. Run the application:
   ```bash
   poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Database Migrations

To create a new migration after changing models:
```bash
docker-compose exec app poetry run alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:
```bash
docker-compose exec app poetry run alembic upgrade head
```
