# Repository Guidelines

## Project Structure & Module Organization
Runtime code lives inside `src/`, with `main.py` exposing the FastAPI app for Uvicorn and `app.py` wiring the NiceGUI router. Configuration helpers stay in `src/config/`, and `database.py` centralizes the async engine/session so repositories under `src/repositories/` stay thin. Persisted shapes belong to SQLAlchemy models in `src/models/`, while request/response contracts live in `src/schemas/`. Service-layer orchestration resides in `src/services/`, and reusable NiceGUI view fragments in `src/ui/`. Database migrations are tracked in `alembic/` with settings in `alembic.ini`. Supporting docs (`docs/`, `ARQUITECTURA.md`, `CAPAS.md`) and helper scripts (`scripts/start-docker.sh`, `scripts/seed_database.py`) round out the toolkit.

## Build, Test, and Development Commands
- `poetry install` — create the virtualenv and pull Python dependencies defined in `pyproject.toml`.
- `poetry run uvicorn src.main:app --reload` — launch the FastAPI + NiceGUI stack with autoreload against your local PostgreSQL.
- `./scripts/start-docker.sh` or `docker-compose up --build` — bring up the full stack (app + db) the same way CI does.
- `docker-compose exec app poetry run alembic upgrade head` — apply migrations to the running containerized database.
- `poetry run pytest` — execute unit/integration tests once they live under `tests/`.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation and exhaustive type hints on public functions. Keep modules small and cohesive: repositories handle persistence, services hold orchestration, and UI modules expose declarative NiceGUI components. Use `snake_case` for Python symbols, `PascalCase` for SQLAlchemy models/Pydantic schemas, and kebab-case for CLI script names. Before opening a PR, run `poetry run black src tests` and `poetry run ruff check src tests` (use `pip install black ruff` inside the env if not already present) so reviewers see clean diffs.

## Testing Guidelines
Pytest is the default harness. Name files `tests/test_<feature>.py` and mirror the `src/` tree so fixtures are easy to find. Prefer async-aware helpers (`pytest.mark.asyncio`) for FastAPI handlers and repositories. Aim for >80% statement coverage, and add regression tests whenever touching `models/` or `services/`. Run `poetry run pytest --maxfail=1 --disable-warnings -q` locally before pushing.

## Commit & Pull Request Guidelines
Commits should be small, described in the imperative (“Add NiceGUI layout shell”, “Fix session cleanup”). Reference the area touched (e.g., `services:`) when helpful. Each PR should include a concise summary, testing notes (`poetry run pytest` output), screenshots or GIFs for UI tweaks, and links to any tracked issues. Keep PRs focused on a single concern so reviewers can reason about backend, UI, and migration changes independently.

## Security & Configuration Tips
Copy `.env.example` to `.env`, fill in secrets, and never commit personalized credentials. When running locally without Docker, ensure `DATABASE_URL` targets a developer database; production values should only live in deployment secrets. Regenerate Alembic migrations whenever models change so environments stay in sync.
