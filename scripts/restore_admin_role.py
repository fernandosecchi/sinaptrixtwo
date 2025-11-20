#!/usr/bin/env python3
"""
Script to restore the Administrator role with all permissions.

Usage:
    docker-compose exec app python scripts/restore_admin_role.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.auth import Role, Permission


async def restore_admin_role():
    """Restore the Administrator role with all permissions."""
    async with AsyncSessionLocal() as session:
        # Check if Administrator role exists
        stmt = select(Role).where(Role.name == "Administrador")
        result = await session.execute(stmt)
        existing_role = result.scalar_one_or_none()

        if existing_role:
            print("❌ El rol Administrador ya existe")
            return False

        # Get ALL permissions
        stmt = select(Permission)
        result = await session.execute(stmt)
        all_permissions = result.scalars().all()

        if not all_permissions:
            print("❌ No hay permisos en el sistema. Ejecuta primero init_roles_permissions.py")
            return False

        # Create Administrator role
        admin_role = Role(
            name="Administrador",
            description="Administrador con acceso completo al sistema",
            is_active=True
        )

        # Assign ALL permissions
        for permission in all_permissions:
            admin_role.permissions.append(permission)

        session.add(admin_role)
        await session.commit()

        print(f"✅ Rol Administrador restaurado con {len(all_permissions)} permisos")
        return True


async def main():
    """Main function."""
    print("\n" + "="*50)
    print("RESTAURANDO ROL ADMINISTRADOR")
    print("="*50 + "\n")

    success = await restore_admin_role()

    print("\n" + "="*50)
    if success:
        print("✅ RESTAURACIÓN COMPLETADA")
    else:
        print("ℹ️  No se necesitó restauración")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())