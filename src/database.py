import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Get database URL from environment variables
# Fallback to a default for development if needed, but better to enforce env var
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/sinaptrixtwo")

# Create the async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("APP_ENV") == "development", # Log SQL in development
)

# Create the async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

async def get_db():
    """Dependency to provide a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
