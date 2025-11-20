#!/usr/bin/env python3
"""
Non-interactive script to create a default superuser.

Usage:
    docker-compose exec app python scripts/create_default_superuser.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.auth import User, Role, Permission
from src.services.auth import AuthService


async def main():
    """Create default superuser without interaction."""
    async with AsyncSessionLocal() as session:
        # Check if admin user exists
        stmt = select(User).where(User.username == "admin")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("Admin user already exists!")
            return

        # Create admin user
        auth_service = AuthService(session)
        hashed_password = auth_service.get_password_hash("admin123")

        admin = User(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            is_superuser=True
        )

        session.add(admin)
        await session.commit()

        print("✅ Default superuser created:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  Please change the password after first login!")


if __name__ == "__main__":
    asyncio.run(main())