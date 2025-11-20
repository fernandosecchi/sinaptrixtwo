#!/usr/bin/env python3
"""
Script to initialize roles and permissions in the database.

Usage:
    docker-compose exec app python scripts/init_roles_permissions.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.auth import Role, Permission


async def create_permissions():
    """Create default permissions for the system."""
    permissions_data = [
        # Dashboard permissions
        {"code": "dashboard:view", "name": "Ver Dashboard", "resource": "dashboard", "action": "view",
         "description": "Permite ver el dashboard principal"},

        # User permissions
        {"code": "user:create", "name": "Crear Usuarios", "resource": "user", "action": "create",
         "description": "Permite crear nuevos usuarios"},
        {"code": "user:read", "name": "Ver Usuarios", "resource": "user", "action": "read",
         "description": "Permite ver la lista de usuarios"},
        {"code": "user:update", "name": "Actualizar Usuarios", "resource": "user", "action": "update",
         "description": "Permite editar usuarios existentes"},
        {"code": "user:delete", "name": "Eliminar Usuarios", "resource": "user", "action": "delete",
         "description": "Permite eliminar usuarios"},

        # Lead permissions
        {"code": "lead:create", "name": "Crear Leads", "resource": "lead", "action": "create",
         "description": "Permite crear nuevos leads"},
        {"code": "lead:read", "name": "Ver Leads", "resource": "lead", "action": "read",
         "description": "Permite ver la lista de leads"},
        {"code": "lead:update", "name": "Actualizar Leads", "resource": "lead", "action": "update",
         "description": "Permite editar leads existentes"},
        {"code": "lead:delete", "name": "Eliminar Leads", "resource": "lead", "action": "delete",
         "description": "Permite eliminar leads"},
        {"code": "lead:convert", "name": "Convertir Leads", "resource": "lead", "action": "convert",
         "description": "Permite convertir leads en clientes"},

        # Role permissions
        {"code": "role:create", "name": "Crear Roles", "resource": "role", "action": "create",
         "description": "Permite crear nuevos roles"},
        {"code": "role:read", "name": "Ver Roles", "resource": "role", "action": "read",
         "description": "Permite ver la lista de roles"},
        {"code": "role:update", "name": "Actualizar Roles", "resource": "role", "action": "update",
         "description": "Permite editar roles existentes"},
        {"code": "role:delete", "name": "Eliminar Roles", "resource": "role", "action": "delete",
         "description": "Permite eliminar roles"},
        {"code": "role:assign", "name": "Asignar Roles", "resource": "role", "action": "assign",
         "description": "Permite asignar roles a usuarios"},
    ]

    async with AsyncSessionLocal() as session:
        created_count = 0

        for perm_data in permissions_data:
            # Check if permission already exists
            stmt = select(Permission).where(Permission.code == perm_data["code"])
            result = await session.execute(stmt)
            existing_perm = result.scalar_one_or_none()

            if not existing_perm:
                permission = Permission(**perm_data)
                session.add(permission)
                created_count += 1
                print(f"✓ Creado permiso: {perm_data['code']}")
            else:
                print(f"  Permiso ya existe: {perm_data['code']}")

        await session.commit()
        print(f"\nTotal permisos creados: {created_count}")
        return created_count


async def create_roles():
    """Create default roles and assign permissions."""
    async with AsyncSessionLocal() as session:
        # Get all permissions
        stmt = select(Permission)
        result = await session.execute(stmt)
        all_permissions = {p.code: p for p in result.scalars().all()}

        roles_data = [
            {
                "name": "Administrador",
                "description": "Administrador con acceso completo al sistema",
                "permission_codes": list(all_permissions.keys())  # All permissions
            },
            {
                "name": "Manager",
                "description": "Manager con acceso a gestión de leads y usuarios",
                "permission_codes": [
                    "dashboard:view",
                    "user:read", "user:update",
                    "lead:create", "lead:read", "lead:update", "lead:delete", "lead:convert",
                    "role:read"
                ]
            },
            {
                "name": "Vendedor",
                "description": "Vendedor con acceso a gestión de leads",
                "permission_codes": [
                    "dashboard:view",
                    "lead:create", "lead:read", "lead:update", "lead:convert"
                ]
            },
            {
                "name": "Viewer",
                "description": "Usuario con acceso de solo lectura",
                "permission_codes": [
                    "dashboard:view",
                    "user:read",
                    "lead:read",
                    "role:read"
                ]
            }
        ]

        created_count = 0

        for role_data in roles_data:
            # Check if role already exists
            stmt = select(Role).where(Role.name == role_data["name"])
            result = await session.execute(stmt)
            existing_role = result.scalar_one_or_none()

            if not existing_role:
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    is_active=True
                )

                # Assign permissions
                for perm_code in role_data["permission_codes"]:
                    if perm_code in all_permissions:
                        role.permissions.append(all_permissions[perm_code])

                session.add(role)
                created_count += 1
                print(f"✓ Creado rol: {role_data['name']} con {len(role_data['permission_codes'])} permisos")
            else:
                print(f"  Rol ya existe: {role_data['name']}")

        await session.commit()
        print(f"\nTotal roles creados: {created_count}")
        return created_count


async def main():
    """Main function to set up roles and permissions."""
    try:
        print("\n" + "="*50)
        print("INICIALIZANDO ROLES Y PERMISOS")
        print("="*50 + "\n")

        # Create permissions
        print("Creando permisos...")
        perm_count = await create_permissions()

        # Create roles
        print("\nCreando roles...")
        role_count = await create_roles()

        print("\n" + "="*50)
        if perm_count > 0 or role_count > 0:
            print("✅ INICIALIZACIÓN COMPLETADA")
        else:
            print("ℹ️  Ya estaba todo inicializado")
        print("="*50)

    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())