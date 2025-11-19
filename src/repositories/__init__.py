"""Repositories package for data access layer."""
from src.repositories.base import BaseRepository
from src.repositories.user_repository import UserRepository
from src.repositories.lead_repository import LeadRepository

__all__ = [
    "BaseRepository",
    "UserRepository", 
    "LeadRepository",
]