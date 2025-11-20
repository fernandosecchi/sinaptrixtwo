#!/usr/bin/env python3
"""
Script to create a superuser and initial roles/permissions.

Usage:
    docker-compose exec app python scripts/create_superuser.py
    or
    poetry run python scripts/create_superuser.py
"""

import asyncio
import sys
import os
from getpass import getpass

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.auth import User, Role, Permission
from src.services.auth import AuthService


async def create_permissions():
    """Create default permissions for the system."""
    permissions_data = [
        # Dashboard permissions
        {"code": "dashboard:view", "name": "View Dashboard", "resource": "dashboard", "action": "view"},
        {"code": "dashboard:edit", "name": "Edit Dashboard", "resource": "dashboard", "action": "edit"},

        # User permissions
        {"code": "user:create", "name": "Create Users", "resource": "user", "action": "create"},
        {"code": "user:read", "name": "View Users", "resource": "user", "action": "read"},
        {"code": "user:update", "name": "Update Users", "resource": "user", "action": "update"},
        {"code": "user:delete", "name": "Delete Users", "resource": "user", "action": "delete"},

        # Lead permissions
        {"code": "lead:create", "name": "Create Leads", "resource": "lead", "action": "create"},
        {"code": "lead:read", "name": "View Leads", "resource": "lead", "action": "read"},
        {"code": "lead:update", "name": "Update Leads", "resource": "lead", "action": "update"},
        {"code": "lead:delete", "name": "Delete Leads", "resource": "lead", "action": "delete"},
        {"code": "lead:convert", "name": "Convert Leads", "resource": "lead", "action": "convert"},

        # Role permissions
        {"code": "role:create", "name": "Create Roles", "resource": "role", "action": "create"},
        {"code": "role:read", "name": "View Roles", "resource": "role", "action": "read"},
        {"code": "role:update", "name": "Update Roles", "resource": "role", "action": "update"},
        {"code": "role:delete", "name": "Delete Roles", "resource": "role", "action": "delete"},

        # Permission management
        {"code": "permission:read", "name": "View Permissions", "resource": "permission", "action": "read"},
        {"code": "permission:assign", "name": "Assign Permissions", "resource": "permission", "action": "assign"},
    ]

    async with AsyncSessionLocal() as session:
        created_permissions = []

        for perm_data in permissions_data:
            # Check if permission already exists
            stmt = select(Permission).where(Permission.code == perm_data["code"])
            result = await session.execute(stmt)
            existing_perm = result.scalar_one_or_none()

            if not existing_perm:
                permission = Permission(
                    code=perm_data["code"],
                    name=perm_data["name"],
                    resource=perm_data["resource"],
                    action=perm_data["action"],
                    description=f"Permission to {perm_data['action']} {perm_data['resource']}"
                )
                session.add(permission)
                created_permissions.append(permission)
                print(f"✓ Created permission: {perm_data['code']}")
            else:
                created_permissions.append(existing_perm)
                print(f"  Permission already exists: {perm_data['code']}")

        await session.commit()
        return created_permissions


async def create_roles(permissions):
    """Create default roles and assign permissions."""
    roles_data = [
        {
            "name": "Admin",
            "description": "Administrator with full access",
            "permission_codes": [p.code for p in permissions]  # All permissions
        },
        {
            "name": "Manager",
            "description": "Manager with lead and user management access",
            "permission_codes": [
                "dashboard:view", "dashboard:edit",
                "user:read", "user:update",
                "lead:create", "lead:read", "lead:update", "lead:delete", "lead:convert"
            ]
        },
        {
            "name": "Sales",
            "description": "Sales team member with lead access",
            "permission_codes": [
                "dashboard:view",
                "lead:create", "lead:read", "lead:update", "lead:convert"
            ]
        },
        {
            "name": "Viewer",
            "description": "Read-only access to system",
            "permission_codes": [
                "dashboard:view",
                "user:read",
                "lead:read"
            ]
        }
    ]

    async with AsyncSessionLocal() as session:
        created_roles = []

        # Get all permissions for mapping
        stmt = select(Permission)
        result = await session.execute(stmt)
        all_permissions = {p.code: p for p in result.scalars().all()}

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
                created_roles.append(role)
                print(f"✓ Created role: {role_data['name']} with {len(role_data['permission_codes'])} permissions")
            else:
                created_roles.append(existing_role)
                print(f"  Role already exists: {role_data['name']}")

        await session.commit()
        return created_roles


async def create_superuser():
    """Create a superuser account."""
    print("\n" + "="*50)
    print("SUPERUSER CREATION")
    print("="*50 + "\n")

    # Get user input
    username = input("Enter username (default: admin): ").strip() or "admin"
    email = input("Enter email (default: admin@example.com): ").strip() or "admin@example.com"
    first_name = input("Enter first name (default: Admin): ").strip() or "Admin"
    last_name = input("Enter last name (default: User): ").strip() or "User"

    # Get password with confirmation
    while True:
        password = getpass("Enter password (min 8 characters): ")
        if len(password) < 8:
            print("Password must be at least 8 characters long!")
            continue

        confirm_password = getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords don't match! Try again.")
            continue

        break

    async with AsyncSessionLocal() as session:
        # Check if user already exists
        stmt = select(User).where(
            (User.username == username) | (User.email == email)
        )
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"\n❌ User with username '{username}' or email '{email}' already exists!")

            if existing_user.is_superuser:
                print("   This user is already a superuser.")
                return existing_user
            else:
                update_choice = input("Would you like to make this user a superuser? (y/n): ").lower()
                if update_choice == 'y':
                    existing_user.is_superuser = True
                    existing_user.is_active = True
                    existing_user.is_verified = True

                    # Assign Admin role
                    stmt = select(Role).where(Role.name == "Admin")
                    result = await session.execute(stmt)
                    admin_role = result.scalar_one_or_none()

                    if admin_role and admin_role not in existing_user.roles:
                        existing_user.roles.append(admin_role)

                    await session.commit()
                    print(f"✓ User '{username}' has been granted superuser privileges!")
                    return existing_user
                else:
                    return None

        # Create new superuser
        auth_service = AuthService(session)
        hashed_password = auth_service.get_password_hash(password)

        superuser = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            is_superuser=True
        )

        # Assign Admin role
        stmt = select(Role).where(Role.name == "Admin")
        result = await session.execute(stmt)
        admin_role = result.scalar_one_or_none()

        if admin_role:
            superuser.roles.append(admin_role)

        session.add(superuser)
        await session.commit()

        print(f"\n✓ Superuser '{username}' created successfully!")
        print(f"  Email: {email}")
        print(f"  Name: {first_name} {last_name}")
        print(f"  Roles: Admin (with all permissions)")

        return superuser


async def main():
    """Main function to set up the authentication system."""
    try:
        print("\n" + "="*50)
        print("SETTING UP AUTHENTICATION SYSTEM")
        print("="*50 + "\n")

        # Create permissions
        print("Creating permissions...")
        permissions = await create_permissions()
        print(f"Total permissions: {len(permissions)}\n")

        # Create roles
        print("Creating roles...")
        roles = await create_roles(permissions)
        print(f"Total roles: {len(roles)}\n")

        # Create superuser
        superuser = await create_superuser()

        if superuser:
            print("\n" + "="*50)
            print("✅ SETUP COMPLETED SUCCESSFULLY!")
            print("="*50)
            print("\nYou can now log in with your superuser credentials.")
            print("Default password for existing users is: changeme123")
        else:
            print("\n⚠️  Setup completed but no superuser was created.")

    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())