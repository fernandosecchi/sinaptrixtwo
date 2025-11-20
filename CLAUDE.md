# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SinaptrixOne is a FastAPI + NiceGUI application with PostgreSQL, using a clean layered architecture. The application combines backend API capabilities (FastAPI) with an integrated web UI (NiceGUI) in a single unified application.

**Tech Stack:**
- Python 3.11
- FastAPI (backend framework)
- NiceGUI (UI framework, natively integrated with FastAPI)
- PostgreSQL (database)
- SQLAlchemy (async ORM)
- Alembic (migrations)
- Poetry (dependency management)
- Docker & Docker Compose (containerization)

## Running the Application

### Docker (Recommended)
```bash
# Start application
./scripts/start-docker.sh
# or
docker-compose up --build

# View logs
docker-compose logs -f app
```

### Local Development
```bash
# Install dependencies
poetry install

# Run application (requires PostgreSQL running)
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Access Points:**
- Application: http://localhost:8000
- Health check: http://localhost:8000/health

## Database Operations

### Migrations
```bash
# Inside Docker container
docker-compose exec app poetry run alembic revision --autogenerate -m "Description"
docker-compose exec app poetry run alembic upgrade head
docker-compose exec app poetry run alembic current

# Local
poetry run alembic revision --autogenerate -m "Description"
poetry run alembic upgrade head
```

### Direct Database Access
```bash
# PostgreSQL CLI
docker-compose exec db psql -U postgres -d sinaptrixtwo

# View tables
docker-compose exec db psql -U postgres -d sinaptrixtwo -c "\dt"
```

## Architecture

This project follows a **strict layered architecture** with clear separation of concerns:

```
UI Layer (NiceGUI)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Model Layer (Database Entities)
    ↓
Database (PostgreSQL)
```

### Key Architecture Rules

1. **Never skip layers**: UI must call Services, Services must call Repositories
2. **No direct database access from UI**: Always go through the service layer
3. **Services contain business logic**: Validation, orchestration, transactions
4. **Repositories handle data access**: All SQL queries live here
5. **Models are POCOs**: Plain classes mapped to database tables

### Directory Structure

```
src/
├── main.py              # FastAPI app + NiceGUI initialization
├── database.py          # Async SQLAlchemy configuration
├── config/
│   └── settings.py      # Centralized configuration (from env vars)
├── models/
│   ├── base.py          # Base class and mixins (TimestampMixin)
│   ├── enums.py         # Enumerations (LeadStatus, LeadSource)
│   ├── user.py          # User model
│   └── lead.py          # Lead model
├── repositories/
│   ├── base.py          # Generic CRUD operations (create, get, update, delete)
│   ├── user_repository.py
│   └── lead_repository.py
├── services/
│   ├── user_service.py  # Business logic for users
│   └── lead_service.py  # Business logic for leads
├── schemas/             # Pydantic models for validation and serialization
│   ├── user.py
│   └── lead.py
└── ui/
    ├── layouts.py       # Shared layout (theme_layout)
    └── pages/           # UI pages
        ├── home.py
        ├── users.py
        └── leads.py
```

## Adding New Features

### 1. Add a New Entity (e.g., "Product")

**a) Create Model**
```python
# src/models/product.py
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin

class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)
```

**b) Export in `src/models/__init__.py`**
```python
from src.models.product import Product
```

**c) Create Repository**
```python
# src/repositories/product_repository.py
from src.repositories.base import BaseRepository
from src.models.product import Product

class ProductRepository(BaseRepository[Product]):
    def __init__(self, session):
        super().__init__(Product, session)

    # Add custom queries if needed
```

**d) Create Service**
```python
# src/services/product_service.py
from src.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, session):
        self.repository = ProductRepository(session)

    async def create_product(self, name: str, price: int):
        # Business logic and validation here
        return await self.repository.create(name=name, price=price)
```

**e) Create Schema (if using API endpoints)**
```python
# src/schemas/product.py
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: int

class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
```

**f) Create Migration**
```bash
docker-compose exec app poetry run alembic revision --autogenerate -m "Add products table"
docker-compose exec app poetry run alembic upgrade head
```

### 2. Add a New UI Page

**a) Create Page File**
```python
# src/ui/pages/products.py
from nicegui import ui
from src.ui.layouts import theme_layout
from src.database import AsyncSessionLocal
from src.services.product_service import ProductService

def create_products_page():
    @ui.page("/products")
    async def products_page():
        with theme_layout('Products'):
            # Use service layer
            async with AsyncSessionLocal() as session:
                service = ProductService(session)
                products = await service.get_all_products()

            # UI implementation
            for product in products:
                ui.label(f"{product.name}: ${product.price}")
```

**b) Register in `src/main.py`**
```python
from src.ui.pages.products import create_products_page

def init_nicegui():
    create_home_page()
    create_leads_page()
    create_users_page()
    create_products_page()  # Add here
```

**c) Add Navigation Link** (optional)
```python
# In src/ui/layouts.py, add to the drawer:
ui.link('Products', '/products').classes('w-full p-4 hover:bg-slate-200 text-slate-800 no-underline')
```

## Important Patterns

### Database Session Management
Always use async context managers:
```python
async with AsyncSessionLocal() as session:
    service = UserService(session)
    result = await service.operation()
```

### Service Pattern
```python
class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def business_operation(self, data):
        # Validation
        if not data.email:
            raise ValueError("Email required")

        # Business logic
        if await self.repository.exists(email=data.email):
            raise ValueError("Email already exists")

        # Create via repository
        return await self.repository.create(**data.dict())
```

### Repository Usage
The `BaseRepository` provides:
- `create(**kwargs)` - Create new record
- `get(id)` - Get by ID
- `get_all(skip, limit, order_by)` - List with pagination
- `update(id, **kwargs)` - Update record
- `delete(id)` - Delete record
- `count()` - Count records
- `exists(**kwargs)` - Check existence
- `filter(**kwargs)` - Filter by criteria

### Configuration
All configuration is centralized in `src/config/settings.py` and loaded from environment variables. Use `.env` file for local development (copy from `.env.example`).

## NiceGUI Integration

NiceGUI is mounted to FastAPI via `ui.run_with()` in `src/main.py`. This means:
- NiceGUI pages are served by the same FastAPI app
- Shared application lifecycle
- NiceGUI pages use `@ui.page()` decorator
- Use `theme_layout()` context manager for consistent styling

## Alembic Configuration

The `alembic/env.py` is configured for async operations and automatically:
- Imports all models from `src.models`
- Uses DATABASE_URL from settings
- Supports autogenerate for migrations

**Important**: Always import new models in `alembic/env.py` for autogenerate to detect them:
```python
from src.models import Base, User, Lead, Product  # Add new models here
```

## Docker Notes

- App container mounts source code as volume for hot-reload
- Database uses persistent volume (`postgres_data`)
- Healthcheck on PostgreSQL ensures app starts after DB is ready
- Use `docker-compose down -v` to completely reset (including DB data)

## Common Issues

### Migrations Not Applied
```bash
# Check current migration status
docker-compose exec app poetry run alembic current

# Apply pending migrations
docker-compose exec app poetry run alembic upgrade head
```

### Import Errors After Adding Models
Ensure the model is:
1. Exported in `src/models/__init__.py`
2. Imported in `alembic/env.py`

### UI Not Reflecting Changes
```bash
# Restart app container (code changes should auto-reload)
docker-compose restart app

# If still not working, rebuild
docker-compose up --build
```
