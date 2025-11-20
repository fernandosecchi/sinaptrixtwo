#!/usr/bin/env python3
"""
Simple script to create a default superuser with minimal dependencies.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.auth import User
import bcrypt


def hash_password(password: str) -> str:
    """Simple password hashing."""
    # Encode and truncate if necessary
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


async def main():
    """Create default superuser without complex auth service."""
    async with AsyncSessionLocal() as session:
        # Check if admin user exists
        stmt = select(User).where(User.username == "admin")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("✅ Admin user already exists!")
            if not existing_user.is_superuser:
                existing_user.is_superuser = True
                existing_user.is_active = True
                existing_user.is_verified = True
                await session.commit()
                print("   Updated to superuser status")
            return

        # Create admin user
        hashed_password = hash_password("admin123")

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

        print("✅ Default superuser created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@example.com")
        print("\n⚠️  IMPORTANT: Please change the password after first login!")
        print("   All existing users have default password: changeme123")


if __name__ == "__main__":
    asyncio.run(main())