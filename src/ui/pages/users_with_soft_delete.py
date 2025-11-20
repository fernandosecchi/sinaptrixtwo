"""Users management page with soft delete and reusable components."""
from datetime import datetime
from typing import List
from nicegui import ui
from sqlalchemy import select, update, or_
from src.database import AsyncSessionLocal
from src.models.auth.user import User
from src.models.auth.role import Role
from src.ui.layouts import theme_layout
from src.ui.components import (
    SearchBar,
    DataTable,
    TableColumn,
    CrudDialog,
    FormField,
    DialogMode,
    ConfirmDialog
)
from src.services.users.user_service import UserService
from src.services.auth.role_service import RoleService


def create_users_page():
    """Register the users management page with reusable components."""

    @ui.page("/usuarios")
    async def users_page():
        breadcrumb_items = [
            ('Gestión', '/'),
            ('Usuarios', '/usuarios')
        ]
        with theme_layout('Usuarios', breadcrumb_items=breadcrumb_items):
            with ui.column().classes('w-full gap-2'):
                # Compact header with add and manage roles buttons
                with ui.row().classes('w-full items-center justify-between mb-2'):
                    with ui.row().classes('gap-2'):
                        ui.button('Nuevo', on_click=lambda: user_dialog.open(DialogMode.CREATE), icon='add').props('size=sm color=primary')
                        ui.button('Gestionar Roles', on_click=lambda: open_user_selector_for_roles(), icon='admin_panel_settings').props('size=sm color=secondary')

                # Search bar component
                async def search_users(search_term: str):
                    await load_users(search_term, update_stats=False)

                async def clear_search():
                    await load_users(None, update_stats=False)

                search_bar = SearchBar(
                    placeholder="Buscar...",
                    on_search=search_users,
                    on_clear=clear_search,
                    search_button_text='',  # Icon only
                    clear_button_text=''     # Icon only
                )

                # Filter toggle and stats in same row
                with ui.row().classes('w-full gap-2 items-center mb-2'):
                    show_deleted = ui.switch('Eliminados').props('size=sm color=negative')
                    show_deleted.on('change', lambda: load_users())

                    ui.space()  # Push stats to the right

                    # Minimal stats container
                    stats_container = ui.row().classes('gap-2 items-center')

                    # Refresh button
                    ui.button(icon='refresh', on_click=lambda: load_users()).props('size=sm flat dense color=gray')

                # Define save_user function before using it
                async def save_user(data: dict, mode: DialogMode):
                    """Save user using the dialog data."""
                    try:
                        async with AsyncSessionLocal() as session:
                            if mode == DialogMode.CREATE:
                                # Check if email already exists
                                result = await session.execute(
                                    select(User).where(User.email == data['email'])
                                )
                                if result.scalar_one_or_none():
                                    ui.notify('El email ya está registrado', type='warning')
                                    return

                                new_user = User(
                                    first_name=data['first_name'],
                                    last_name=data['last_name'],
                                    email=data['email']
                                )
                                session.add(new_user)
                                message = f'Usuario {data["first_name"]} {data["last_name"]} creado exitosamente'
                            else:  # EDIT mode
                                stmt = (
                                    update(User)
                                    .where(User.id == data['id'])
                                    .values(
                                        first_name=data['first_name'],
                                        last_name=data['last_name'],
                                        email=data['email'],
                                        updated_at=datetime.utcnow()
                                    )
                                )
                                await session.execute(stmt)
                                message = f'Usuario actualizado exitosamente'

                            await session.commit()

                        ui.notify(message, type='positive')
                        await load_users()
                    except Exception as e:
                        ui.notify(f'Error: {e}', type='negative')

                async def delete_user(data: dict):
                    """Soft delete a user."""
                    try:
                        async with AsyncSessionLocal() as session:
                            stmt = (
                                update(User)
                                .where(User.id == data['id'])
                                .values(
                                    deleted_at=datetime.utcnow(),
                                    is_deleted=True
                                )
                            )
                            await session.execute(stmt)
                            await session.commit()
                            ui.notify('Usuario eliminado exitosamente', type='info')
                            await load_users()
                    except Exception as e:
                        ui.notify(f'Error: {e}', type='negative')

                # Role management dialog
                role_dialog = ui.dialog()
                with role_dialog, ui.card().classes('w-[600px]'):
                    role_dialog_title = ui.label('').classes('text-xl font-semibold mb-4')

                    # Hidden user ID
                    role_user_id = ui.input().props('hidden')

                    # User info display
                    user_info_label = ui.label('').classes('text-gray-600 mb-4')

                    ui.separator()

                    # Current roles section
                    ui.label('Roles Actuales').classes('text-lg font-medium mb-2')
                    current_roles_container = ui.column().classes('w-full gap-2 mb-4')

                    ui.separator()

                    # Available roles section
                    ui.label('Roles Disponibles').classes('text-lg font-medium mb-2')
                    available_roles_container = ui.column().classes('w-full gap-2')

                    # Actions
                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cerrar', on_click=role_dialog.close).props('flat')

                # User selector dialog for roles
                user_selector_dialog = ui.dialog()
                with user_selector_dialog, ui.card().classes('w-[500px]'):
                    ui.label('Seleccionar Usuario para Gestionar Roles').classes('text-xl font-semibold mb-4')
                    ui.separator()

                    # User list container
                    user_list_container = ui.column().classes('w-full gap-2 max-h-96 overflow-y-auto')

                    # Actions
                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancelar', on_click=user_selector_dialog.close).props('flat')

                async def open_user_selector_for_roles():
                    """Open dialog to select a user for role management."""
                    user_list_container.clear()

                    async with AsyncSessionLocal() as session:
                        stmt = select(User).where(User.deleted_at.is_(None))
                        result = await session.execute(stmt)
                        users = result.scalars().all()

                    with user_list_container:
                        for user in users:
                            with ui.card().classes('w-full cursor-pointer hover:bg-cyan-50 transition-colors'):
                                with ui.row().classes('w-full items-center justify-between'):
                                    with ui.column().classes('gap-0'):
                                        ui.label(f'{user.first_name} {user.last_name}').classes('font-medium')
                                        ui.label(user.email).classes('text-sm text-gray-600')
                                    ui.button(
                                        'Gestionar Roles',
                                        icon='settings',
                                        on_click=lambda u=user: [
                                            user_selector_dialog.close(),
                                            manage_user_roles({
                                                'id': u.id,
                                                'first_name': u.first_name,
                                                'last_name': u.last_name,
                                                'email': u.email
                                            })
                                        ]
                                    ).props('size=sm color=secondary')

                    user_selector_dialog.open()

                async def manage_user_roles(user_data):
                    """Open dialog to manage user roles."""
                    role_user_id.value = str(user_data['id'])
                    role_dialog_title.text = 'Gestionar Roles de Usuario'
                    user_info_label.text = f"Usuario: {user_data['first_name']} {user_data['last_name']} ({user_data['email']})"

                    # Load current user roles and all available roles
                    async with AsyncSessionLocal() as session:
                        user_service = UserService(session)
                        role_service = RoleService(session)

                        # Get user with roles
                        user = await user_service.get_user(user_data['id'])
                        all_roles = await role_service.get_all_roles()

                        # Get current role names
                        current_role_names = [r.name for r in user.roles] if user.roles else []

                    # Clear and populate current roles
                    current_roles_container.clear()
                    with current_roles_container:
                        if current_role_names:
                            for role_name in current_role_names:
                                with ui.row().classes('items-center gap-2'):
                                    ui.chip(role_name, icon='verified_user').props('color=primary')
                                    ui.button(
                                        icon='remove_circle',
                                        on_click=lambda r=role_name: remove_role_from_user(user_data['id'], r)
                                    ).props('flat round dense color=negative').tooltip('Quitar rol')
                        else:
                            ui.label('Sin roles asignados').classes('text-gray-500 italic')

                    # Clear and populate available roles
                    available_roles_container.clear()
                    with available_roles_container:
                        available_count = 0
                        for role in all_roles:
                            if role.name not in current_role_names:
                                available_count += 1
                                with ui.row().classes('items-center gap-2'):
                                    ui.chip(role.name, icon='badge').props('outline')
                                    ui.label(f'({len(role.permissions)} permisos)').classes('text-sm text-gray-500')
                                    ui.button(
                                        icon='add_circle',
                                        on_click=lambda r=role.name: add_role_to_user(user_data['id'], r)
                                    ).props('flat round dense color=positive').tooltip('Asignar rol')

                        if available_count == 0:
                            ui.label('Todos los roles ya están asignados').classes('text-gray-500 italic')

                    role_dialog.open()

                async def add_role_to_user(user_id: int, role_name: str):
                    """Add a role to a user."""
                    try:
                        async with AsyncSessionLocal() as session:
                            user_service = UserService(session)
                            await user_service.assign_role(user_id, role_name)

                        ui.notify(f'Rol {role_name} asignado exitosamente', type='positive')

                        # Refresh the dialog
                        role_dialog.close()
                        # Reload user data and reopen dialog
                        user_row = {'id': user_id}
                        async with AsyncSessionLocal() as session:
                            user = await session.get(User, user_id)
                            user_row.update({
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'email': user.email
                            })
                        await manage_user_roles(user_row)

                    except Exception as e:
                        ui.notify(f'Error al asignar rol: {str(e)}', type='negative')

                async def remove_role_from_user(user_id: int, role_name: str):
                    """Remove a role from a user."""
                    try:
                        async with AsyncSessionLocal() as session:
                            user_service = UserService(session)
                            await user_service.remove_role(user_id, role_name)

                        ui.notify(f'Rol {role_name} removido exitosamente', type='info')

                        # Refresh the dialog
                        role_dialog.close()
                        # Reload user data and reopen dialog
                        user_row = {'id': user_id}
                        async with AsyncSessionLocal() as session:
                            user = await session.get(User, user_id)
                            user_row.update({
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'email': user.email
                            })
                        await manage_user_roles(user_row)

                    except Exception as e:
                        ui.notify(f'Error al remover rol: {str(e)}', type='negative')

                # Create user dialog after defining the functions
                user_dialog = CrudDialog(
                    title="Usuario",
                    fields=[
                        FormField('first_name', 'Nombre', required=True, full_width=False),
                        FormField('last_name', 'Apellido', required=True, full_width=False),
                        FormField('email', 'Email', field_type='email', required=True)
                    ],
                    on_save=save_user,
                    on_delete=delete_user,
                    width='w-[500px]'
                )

                # Data table with columns
                columns = [
                    TableColumn('id', 'ID', 'id'),
                    TableColumn('first_name', 'Nombre', 'first_name'),
                    TableColumn('last_name', 'Apellido', 'last_name'),
                    TableColumn('email', 'Email', 'email'),
                    TableColumn('is_active', 'Estado', 'is_active', format_fn=lambda x: 'Activo' if x else 'Inactivo'),
                    TableColumn('created_at', 'Creado', 'created_at', format_fn=lambda x: x.strftime("%d/%m/%Y") if x else ''),
                ]

                # Create table without custom_actions (not supported)
                data_table = DataTable(
                    title="",
                    columns=columns,
                    rows_per_page=10,
                    on_view=lambda row: view_user(row),
                    on_edit=lambda row: edit_user(row),
                    on_delete=lambda row: confirm_delete(row),
                    searchable_fields=['first_name', 'last_name', 'email'],
                    show_stats=False
                )

                def view_user(row):
                    """View user details."""
                    user_dialog.open(DialogMode.VIEW, row)

                def edit_user(row):
                    """Edit user."""
                    user_dialog.open(DialogMode.EDIT, row)

                def confirm_delete(row):
                    """Confirm user deletion."""
                    if row.get('deleted_at'):
                        async def restore_user():
                            try:
                                async with AsyncSessionLocal() as session:
                                    stmt = (
                                        update(User)
                                        .where(User.id == row['id'])
                                        .values(
                                            deleted_at=None,
                                            is_deleted=False
                                        )
                                    )
                                    await session.execute(stmt)
                                    await session.commit()
                                    ui.notify('Usuario restaurado exitosamente', type='positive')
                                    await load_users()
                            except Exception as e:
                                ui.notify(f'Error: {e}', type='negative')

                        ConfirmDialog.ask(
                            title='Restaurar Usuario',
                            message=f'¿Deseas restaurar al usuario {row["first_name"]} {row["last_name"]}?',
                            on_confirm=restore_user,
                            confirm_text='Restaurar',
                            confirm_color='positive'
                        )
                    else:
                        ConfirmDialog.ask(
                            title='Eliminar Usuario',
                            message=f'¿Estás seguro de eliminar al usuario {row["first_name"]} {row["last_name"]}?',
                            on_confirm=lambda: delete_user(row),
                            confirm_color='negative',
                            icon='warning',
                            icon_color='red'
                        )

                async def load_stats():
                    """Load and display minimal user statistics."""
                    try:
                        async with AsyncSessionLocal() as session:
                            # Get all users
                            result = await session.execute(select(User))
                            all_users = result.scalars().all()

                            # Calculate stats
                            total = len(all_users)
                            active = sum(1 for u in all_users if u.is_active and not u.deleted_at)
                            inactive = sum(1 for u in all_users if not u.is_active and not u.deleted_at)
                            deleted = sum(1 for u in all_users if u.deleted_at)

                            # Clear and recreate minimal stats
                            stats_container.clear()

                            with stats_container:
                                # Ultra compact stats - just numbers with tooltips
                                ui.label(f'{total}').classes('text-xs text-gray-600').tooltip('Total')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{active}').classes('text-xs text-green-600').tooltip('Activos')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{inactive}').classes('text-xs text-orange-600').tooltip('Inactivos')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{deleted}').classes('text-xs text-red-600').tooltip('Eliminados')

                    except Exception as e:
                        ui.notify(f'Error al cargar estadísticas: {e}', type='negative')

                async def load_users(search_term: str = None, update_stats: bool = True):
                    """Load and display users in the table."""
                    # Only update stats on initial load or explicit request
                    if update_stats:
                        await load_stats()

                    try:
                        async with AsyncSessionLocal() as session:
                            # Create base query
                            query = select(User)

                            # Apply deleted filter
                            if show_deleted.value:
                                query = query.where(User.deleted_at.is_not(None))
                            else:
                                query = query.where(User.deleted_at.is_(None))

                            # Apply search filter if present
                            if search_term:
                                search_pattern = f"%{search_term}%"
                                query = query.where(
                                    or_(
                                        User.first_name.ilike(search_pattern),
                                        User.last_name.ilike(search_pattern),
                                        User.email.ilike(search_pattern)
                                    )
                                )

                            # Execute query
                            result = await session.execute(query.order_by(User.created_at.desc()))
                            users = result.scalars().all()

                            # Convert to dict for table
                            users_data = []
                            for user in users:
                                users_data.append({
                                    'id': user.id,
                                    'first_name': user.first_name,
                                    'last_name': user.last_name,
                                    'email': user.email,
                                    'is_active': user.is_active,
                                    'created_at': user.created_at,
                                    'updated_at': user.updated_at,
                                    'deleted_at': user.deleted_at
                                })

                            # Load data into table
                            data_table.load_data(users_data)

                    except Exception as e:
                        ui.notify(f'Error al cargar usuarios: {e}', type='negative')

                # Load initial data
                await load_users()