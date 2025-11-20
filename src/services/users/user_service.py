"""User service for business logic operations."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.users.user_repository import UserRepository
from src.repositories.auth.role_repository import RoleRepository
from src.models.auth.user import User


class UserService:
    """Service layer for user operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize user service with database session."""
        self.repository = UserRepository(session)
        self.role_repository = RoleRepository(session)
    
    async def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str
    ) -> User:
        """Create a new user with validation."""
        # Check if email already exists
        if await self.repository.email_exists(email):
            raise ValueError(f"El email {email} ya está registrado")
        
        # Create user
        return await self.repository.create(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.repository.get(user_id)
    
    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[User]:
        """Get all users with pagination (active by default)."""
        if include_deleted:
            return await self.repository.get_all(
                skip=skip,
                limit=limit,
                order_by=User.created_at.desc()
            )
        else:
            return await self.repository.get_all_active(
                skip=skip,
                limit=limit
            )
    
    async def update_user(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None
    ) -> Optional[User]:
        """Update user information."""
        # Check if email is being changed and if it's already taken
        if email:
            if await self.repository.email_exists(email, exclude_id=user_id):
                raise ValueError(f"El email {email} ya está registrado")
        
        # Build update data
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if email is not None:
            update_data["email"] = email
        
        if not update_data:
            return await self.get_user(user_id)
        
        return await self.repository.update(user_id, **update_data)
    
    async def delete_user(self, user_id: int) -> bool:
        """Soft delete a user."""
        return await self.repository.soft_delete(user_id)
    
    async def hard_delete_user(self, user_id: int) -> bool:
        """Permanently delete a user from database."""
        return await self.repository.hard_delete(user_id)
    
    async def restore_user(self, user_id: int) -> bool:
        """Restore a soft-deleted user."""
        return await self.repository.restore(user_id)
    
    async def search_users(self, search_term: str, include_deleted: bool = False) -> List[User]:
        """Search users by name or email."""
        if not search_term:
            return await self.get_all_users(include_deleted=include_deleted)
        return await self.repository.search(search_term, include_deleted=include_deleted)
    
    async def get_user_by_email(self, email: str, include_deleted: bool = False) -> Optional[User]:
        """Get user by email address."""
        return await self.repository.get_by_email(email, include_deleted=include_deleted)
    
    async def get_deleted_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get all soft-deleted users."""
        return await self.repository.get_all_deleted(
            skip=skip,
            limit=limit
        )
    
    async def get_users_count(self) -> int:
        """Get total count of users."""
        return await self.repository.count()
    
    async def validate_user_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Validate user data and return errors if any."""
        errors = {}
        
        if not data.get("first_name"):
            errors["first_name"] = "El nombre es requerido"
        elif len(data["first_name"]) > 50:
            errors["first_name"] = "El nombre no puede tener más de 50 caracteres"
        
        if not data.get("last_name"):
            errors["last_name"] = "El apellido es requerido"
        elif len(data["last_name"]) > 50:
            errors["last_name"] = "El apellido no puede tener más de 50 caracteres"
        
        if not data.get("email"):
            errors["email"] = "El email es requerido"
        elif "@" not in data["email"]:
            errors["email"] = "El email no es válido"
        elif len(data["email"]) > 255:
            errors["email"] = "El email no puede tener más de 255 caracteres"
        
        return errors

    async def assign_role(self, user_id: int, role_name: str) -> bool:
        """Assign a role to a user."""
        user = await self.repository.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
            
        role = await self.role_repository.get_by_name(role_name)
        if not role:
            raise ValueError(f"El rol '{role_name}' no existe")
            
        # Check if user already has the role
        if any(r.name == role_name for r in user.roles):
            return True
            
        user.roles.append(role)
        await self.repository.session.commit()
        return True

    async def remove_role(self, user_id: int, role_name: str) -> bool:
        """Remove a role from a user."""
        user = await self.repository.get(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
            
        role = await self.role_repository.get_by_name(role_name)
        if not role:
            return False
            
        # Check if user has the role
        user_role = next((r for r in user.roles if r.name == role_name), None)
        if not user_role:
            return False
            
        user.roles.remove(user_role)
        await self.repository.session.commit()
        return True