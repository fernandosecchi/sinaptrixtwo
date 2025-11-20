"""Authentication middleware for protecting routes."""
from typing import Callable, Optional, List
from nicegui import ui, app
from functools import wraps


def require_auth(
    redirect_to: str = '/login',
    roles: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None
):
    """
    Decorator to require authentication for a page.

    Args:
        redirect_to: Where to redirect if not authenticated
        roles: Required roles (user must have at least one)
        permissions: Required permissions (user must have all)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if user is authenticated
            if not app.storage.user.get('authenticated'):
                ui.notify('Por favor inicia sesión para acceder a esta página', type='warning')
                ui.navigate.to(redirect_to)
                return

            # Check roles if specified
            if roles:
                user_roles = app.storage.user.get('roles', [])
                is_superuser = app.storage.user.get('is_superuser', False)

                if not is_superuser and not any(role in user_roles for role in roles):
                    ui.notify('No tienes permisos para acceder a esta página', type='negative')
                    ui.navigate.to('/')
                    return

            # Check permissions if specified
            if permissions:
                # For now, we'll skip permission checking as it requires
                # loading permissions from the database
                # This can be implemented later with a permission service
                pass

            # User is authorized, call the original function
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

        return wrapper
    return decorator


def check_auth() -> bool:
    """Check if the current user is authenticated."""
    return app.storage.user.get('authenticated', False)


def get_current_user() -> Optional[dict]:
    """Get the current authenticated user information."""
    if check_auth():
        return {
            'id': app.storage.user.get('user_id'),
            'username': app.storage.user.get('username'),
            'email': app.storage.user.get('email'),
            'full_name': app.storage.user.get('full_name'),
            'is_superuser': app.storage.user.get('is_superuser', False),
            'roles': app.storage.user.get('roles', [])
        }
    return None


def has_role(role: str) -> bool:
    """Check if the current user has a specific role."""
    if not check_auth():
        return False

    if app.storage.user.get('is_superuser'):
        return True

    user_roles = app.storage.user.get('roles', [])
    return role in user_roles


def is_superuser() -> bool:
    """Check if the current user is a superuser."""
    return check_auth() and app.storage.user.get('is_superuser', False)


# Import asyncio for async function detection
import asyncio


# Create a context manager for protected pages
class AuthRequired:
    """Context manager for protecting page content."""

    def __init__(self, redirect_to: str = '/login', message: str = None):
        self.redirect_to = redirect_to
        self.message = message or 'Por favor inicia sesión para acceder a esta página'
        self.authorized = False

    def __enter__(self):
        """Check authentication on entering context."""
        if not check_auth():
            ui.notify(self.message, type='warning')
            ui.navigate.to(self.redirect_to)
            self.authorized = False
        else:
            self.authorized = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up on exit."""
        pass