"""Dashboard page with authentication required."""
from nicegui import ui, app
from src.ui.layouts import theme_layout
from src.ui.auth_middleware import require_auth, get_current_user


def create_dashboard_page():
    """Register the dashboard page with authentication."""

    @ui.page("/dashboard")
    @require_auth()
    async def dashboard_page():
        # Get current user info
        current_user = get_current_user()

        with theme_layout('Dashboard'):
            with ui.column().classes('w-full gap-6'):
                # Welcome message
                with ui.card().classes('w-full p-6 bg-gradient-to-r from-blue-500 to-indigo-600 text-white'):
                    ui.label(f'¡Bienvenido, {current_user["full_name"]}!').classes('text-2xl font-bold')
                    ui.label(f'Usuario: {current_user["username"]} | Email: {current_user["email"]}').classes('text-sm opacity-90 mt-2')

                    if current_user["is_superuser"]:
                        ui.label('👑 Superusuario').classes('text-sm mt-2')
                    elif current_user["roles"]:
                        ui.label(f'Roles: {", ".join(current_user["roles"])}').classes('text-sm mt-2')

                # Quick stats
                with ui.row().classes('w-full gap-4'):
                    with ui.card().classes('flex-1 p-6'):
                        ui.icon('people', size='lg').classes('text-blue-500 mb-2')
                        ui.label('Usuarios').classes('text-sm text-gray-600')
                        ui.label('0').classes('text-3xl font-bold')

                    with ui.card().classes('flex-1 p-6'):
                        ui.icon('contacts', size='lg').classes('text-green-500 mb-2')
                        ui.label('Leads').classes('text-sm text-gray-600')
                        ui.label('0').classes('text-3xl font-bold')

                    with ui.card().classes('flex-1 p-6'):
                        ui.icon('trending_up', size='lg').classes('text-orange-500 mb-2')
                        ui.label('Conversión').classes('text-sm text-gray-600')
                        ui.label('0%').classes('text-3xl font-bold')

                    with ui.card().classes('flex-1 p-6'):
                        ui.icon('assessment', size='lg').classes('text-purple-500 mb-2')
                        ui.label('Actividad').classes('text-sm text-gray-600')
                        ui.label('0').classes('text-3xl font-bold')

                # Quick actions
                with ui.card().classes('w-full p-6'):
                    ui.label('Acciones Rápidas').classes('text-lg font-semibold mb-4')

                    with ui.row().classes('gap-4'):
                        ui.button('Nuevo Lead', icon='person_add', on_click=lambda: ui.navigate.to('/leads')).props('color=primary')
                        ui.button('Ver Usuarios', icon='people', on_click=lambda: ui.navigate.to('/usuarios')).props('color=secondary')
                        ui.button('Mi Perfil', icon='account_circle', on_click=lambda: ui.navigate.to('/profile')).props('flat')
                        ui.button('Cerrar Sesión', icon='logout', on_click=lambda: ui.navigate.to('/logout')).props('flat color=negative')

                # Recent activity placeholder
                with ui.card().classes('w-full p-6'):
                    ui.label('Actividad Reciente').classes('text-lg font-semibold mb-4')
                    ui.label('No hay actividad reciente').classes('text-gray-500 italic')