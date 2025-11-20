"""Login page for user authentication."""
from nicegui import ui, app
from src.database import AsyncSessionLocal
from src.services.auth import AuthService


def create_login_page():
    """Create the login page for user authentication."""

    @ui.page("/login")
    async def login_page():
        # Clear any existing auth session
        app.storage.user.clear()

        # Center the login form
        with ui.element('div').classes('w-full min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100'):
            with ui.card().classes('w-full max-w-sm p-6'):
                # Logo and title
                with ui.column().classes('w-full items-center mb-6'):
                    ui.icon('lock', size='lg').classes('text-indigo-600 mb-2')
                    ui.label('SinaptrixOne').classes('text-2xl font-bold text-gray-800')
                    ui.label('Iniciar Sesión').classes('text-sm text-gray-600')

                # Login form
                with ui.column().classes('w-full gap-4'):
                    # Username/Email input
                    username_input = ui.input(
                        'Usuario o Email',
                        placeholder='admin'
                    ).props('outlined dense').classes('w-full')
                    username_input.props('prepend-inner-icon=person')

                    # Password input
                    password_input = ui.input(
                        'Contraseña',
                        password=True,
                        password_toggle_button=True
                    ).props('outlined dense').classes('w-full')
                    password_input.props('prepend-inner-icon=lock')

                    # Remember me checkbox
                    remember_me = ui.checkbox('Recordarme').classes('mt-2')

                    # Error message container
                    error_container = ui.column().classes('w-full')

                    # Login button
                    async def handle_login():
                        # Clear previous errors
                        error_container.clear()

                        # Validate inputs
                        if not username_input.value:
                            with error_container:
                                ui.label('Por favor ingresa tu usuario o email').classes('text-red-500 text-sm')
                            return

                        if not password_input.value:
                            with error_container:
                                ui.label('Por favor ingresa tu contraseña').classes('text-red-500 text-sm')
                            return

                        # Show loading state
                        login_button.disable()
                        login_button.text = 'Iniciando sesión...'

                        try:
                            async with AsyncSessionLocal() as session:
                                auth_service = AuthService(session)

                                # Authenticate user
                                user = await auth_service.authenticate_user(
                                    username_input.value,
                                    password_input.value
                                )

                                if user:
                                    # Create tokens
                                    access_token_data = {
                                        "user_id": user.id,
                                        "username": user.username,
                                        "email": user.email,
                                        "is_superuser": user.is_superuser,
                                        "roles": [role.name for role in user.roles]
                                    }

                                    access_token = auth_service.create_access_token(access_token_data)
                                    refresh_token = await auth_service.create_refresh_token(user)

                                    # Store in session
                                    app.storage.user['authenticated'] = True
                                    app.storage.user['user_id'] = user.id
                                    app.storage.user['username'] = user.username
                                    app.storage.user['email'] = user.email
                                    app.storage.user['full_name'] = user.full_name
                                    app.storage.user['is_superuser'] = user.is_superuser
                                    app.storage.user['access_token'] = access_token
                                    app.storage.user['refresh_token'] = refresh_token
                                    app.storage.user['roles'] = [role.name for role in user.roles]

                                    # Show success message
                                    ui.notify(f'¡Bienvenido {user.first_name}!', type='positive')

                                    # Redirect to dashboard or home
                                    ui.navigate.to('/dashboard')
                                else:
                                    # Authentication failed
                                    with error_container:
                                        ui.label('Usuario o contraseña incorrectos').classes('text-red-500 text-sm')

                                    # Reset button state
                                    login_button.enable()
                                    login_button.text = 'Iniciar Sesión'

                        except Exception as e:
                            with error_container:
                                ui.label(f'Error al iniciar sesión: {str(e)}').classes('text-red-500 text-sm')

                            # Reset button state
                            login_button.enable()
                            login_button.text = 'Iniciar Sesión'

                    login_button = ui.button(
                        'Iniciar Sesión',
                        on_click=handle_login
                    ).props('color=primary').classes('w-full mt-3')

                    # Handle Enter key press
                    password_input.on('keydown.enter', handle_login)

                # Divider
                with ui.row().classes('w-full items-center my-4'):
                    ui.element('div').classes('flex-1 h-px bg-gray-300')
                    ui.label('o').classes('px-3 text-gray-500 text-xs')
                    ui.element('div').classes('flex-1 h-px bg-gray-300')

                # Additional options
                with ui.column().classes('w-full items-center gap-1'):
                    ui.link('¿Olvidaste tu contraseña?', '/forgot-password').classes('text-xs text-indigo-600 hover:text-indigo-700')

                # Footer info
                with ui.column().classes('w-full items-center mt-4 pt-3 border-t'):
                    ui.label('© 2024 SinaptrixOne').classes('text-xs text-gray-500')
                    with ui.row().classes('gap-1 text-xs'):
                        ui.label('Demo:').classes('text-gray-500')
                        ui.label('admin / admin123').classes('text-gray-600 font-mono text-xs')


def create_logout_page():
    """Create the logout page."""

    @ui.page("/logout")
    async def logout_page():
        # Clear user session
        if app.storage.user.get('refresh_token'):
            try:
                async with AsyncSessionLocal() as session:
                    auth_service = AuthService(session)
                    await auth_service.revoke_refresh_token(
                        app.storage.user['refresh_token'],
                        reason="User logout"
                    )
            except:
                pass  # Ignore errors during logout

        # Clear storage
        app.storage.user.clear()

        # Create a temporary page that redirects
        with ui.element('div').classes('w-full min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100'):
            with ui.card().classes('w-96 p-8 text-center'):
                ui.icon('logout', size='xl').classes('text-indigo-600 mb-4')
                ui.label('Cerrando sesión...').classes('text-xl font-semibold text-gray-800 mb-2')
                ui.label('Serás redirigido al login').classes('text-sm text-gray-600')
                ui.spinner(size='lg').classes('mt-4')

        # Show notification
        ui.notify('Has cerrado sesión exitosamente', type='info', position='top')

        # Redirect after a short delay
        ui.timer(1.5, lambda: ui.navigate.to('/login'), once=True)