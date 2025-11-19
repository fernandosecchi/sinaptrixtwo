"""Application configuration settings."""
import os
from typing import Optional
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/sinaptrixtwo"
    )
    
    # Application
    APP_NAME: str = "SinaptrixTwo"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = APP_ENV == "development"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = APP_ENV == "development"
    
    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "change-this-secret-in-production"
    )
    
    # NiceGUI
    STORAGE_SECRET: str = os.getenv(
        "STORAGE_SECRET",
        "change-this-secret-in-production"
    )
    
    # PostgreSQL
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "sinaptrixtwo")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENV == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.APP_ENV == "testing"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()