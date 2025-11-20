"""Role management page with granular permission control."""
from datetime import datetime
from typing import List, Dict
from nicegui import ui
from src.database import AsyncSessionLocal
from src.services.auth.role_service import RoleService
from src.schemas.auth.role import RoleCreate, RoleUpdate
from src.ui.layouts import theme_layout


def create_roles_page():
    """Register the roles page route with complete CRUD functionality."""

    @ui.page("/roles")
    async def roles_page():
        with theme_layout('Gestión de Roles'):
            with ui.column().classes('w-full max-w-7xl gap-4'):
                # Header with title and add button
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label('Roles y Permisos').classes('text-3xl font-bold text-primary')
                    ui.button('Nuevo Rol', on_click=lambda: show_role_dialog(), icon='add_moderator').props('color=primary')

                # Role list container
                roles_container = ui.column().classes('w-full gap-4')

                # Role Dialog
                role_dialog = ui.dialog()
                with role_dialog, ui.card().classes('w-[800px] max-w-full h-[90vh]'):
                    dialog_title = ui.label('').classes('text-xl font-semibold mb-4')

                    # Hidden ID for edit mode
                    role_id_input = ui.input().props('hidden')

                    # System role info message (initially hidden)
                    system_info_container = ui.column().classes('w-full')

                    # Form container with scroll
                    with ui.scroll_area().classes('h-full flex-1'):
                        with ui.column().classes('w-full gap-4 pr-4'):
                            # Basic Info
                            ui.label('Información Básica').classes('text-lg font-medium text-gray-600')
                            name_input = ui.input('Nombre del Rol *').props('outlined dense').classes('w-full')
                            desc_input = ui.textarea('Descripción').props('outlined dense rows=2').classes('w-full')
                            
                            ui.separator().classes('my-2')

                            # Permissions
                            ui.label('Asignación de Permisos').classes('text-lg font-medium text-gray-600')
                            permissions_container = ui.column().classes('w-full gap-4')

                    # Actions
                    with ui.row().classes('w-full justify-end gap-2 mt-4 pt-4 border-t'):
                        ui.button('Cancelar', on_click=role_dialog.close).props('flat')
                        save_btn = ui.button('Guardar', on_click=lambda: save_role()).props('color=primary')

                # Permission state tracking
                permission_checkboxes = {}  # Store checkbox references by permission ID

                async def load_permissions_into_dialog(selected_ids: List[int] = None):
                    """Load and render permissions grouped by resource."""
                    permissions_container.clear()
                    permission_checkboxes.clear()
                    selected_ids = selected_ids or []

                    async with AsyncSessionLocal() as session:
                        service = RoleService(session)
                        permissions = await service.get_all_permissions()

                    # Group by resource
                    grouped = {}
                    for p in permissions:
                        if p.resource not in grouped:
                            grouped[p.resource] = []
                        grouped[p.resource].append(p)

                    # Render groups
                    with permissions_container:
                        for resource, perms in grouped.items():
                            with ui.expansion(resource.upper(), icon='category').classes('w-full border rounded-lg').props('default-opened'):
                                with ui.row().classes('w-full gap-4 p-2 flex-wrap'):
                                    for p in perms:
                                        cb = ui.checkbox(
                                            f"{p.action} ({p.description or ''})", 
                                            value=p.id in selected_ids
                                        )
                                        permission_checkboxes[p.id] = cb

                def show_role_dialog(role=None):
                    """Open dialog for create or edit."""
                    name_input.value = ''
                    desc_input.value = ''
                    role_id_input.value = ''

                    # Clear system info container
                    system_info_container.clear()

                    # Define system roles
                    SYSTEM_ROLES = ['Administrador', 'Manager', 'Vendedor', 'Viewer']

                    if role:
                        is_system_role = role.name in SYSTEM_ROLES

                        if is_system_role:
                            dialog_title.text = f'Editar Rol del Sistema: {role.name}'
                            # For system roles, disable name editing but allow permission changes
                            name_input.props('readonly')
                            name_input.tooltip('Los nombres de roles del sistema no se pueden cambiar')

                            # Show system role info
                            with system_info_container:
                                with ui.card().classes('w-full bg-blue-50 border-blue-300'):
                                    with ui.row().classes('items-center gap-2'):
                                        ui.icon('info', color='blue')
                                        with ui.column().classes('gap-0'):
                                            ui.label('Rol del Sistema').classes('font-semibold text-blue-900')
                                            ui.label('Puedes modificar los permisos pero no el nombre del rol.').classes('text-sm text-blue-700')
                        else:
                            dialog_title.text = 'Editar Rol'
                            name_input.props(remove='readonly')

                        role_id_input.value = str(role.id)
                        name_input.value = role.name
                        desc_input.value = role.description or ''
                        # Get permission IDs
                        current_perm_ids = [p.id for p in role.permissions]
                    else:
                        dialog_title.text = 'Nuevo Rol'
                        name_input.props(remove='readonly')
                        current_perm_ids = []

                    # Load permissions asynchronously then open
                    async def prepare_dialog():
                        await load_permissions_into_dialog(current_perm_ids)
                        role_dialog.open()

                    prepare_dialog()

                async def save_role():
                    """Save or update role."""
                    if not name_input.value:
                        ui.notify('El nombre del rol es requerido', type='warning')
                        return

                    # Collect selected permissions
                    selected_perms = [pid for pid, cb in permission_checkboxes.items() if cb.value]

                    try:
                        async with AsyncSessionLocal() as session:
                            service = RoleService(session)
                            
                            if role_id_input.value: # Edit
                                await service.update_role(
                                    int(role_id_input.value),
                                    RoleUpdate(
                                        name=name_input.value,
                                        description=desc_input.value,
                                        permission_ids=selected_perms
                                    )
                                )
                                ui.notify('Rol actualizado exitosamente', type='positive')
                            else: # Create
                                await service.create_role(
                                    RoleCreate(
                                        name=name_input.value,
                                        description=desc_input.value,
                                        permission_ids=selected_perms
                                    )
                                )
                                ui.notify('Rol creado exitosamente', type='positive')

                        role_dialog.close()
                        await load_roles()

                    except ValueError as e:
                        ui.notify(str(e), type='warning')
                    except Exception as e:
                        ui.notify(f'Error inesperado: {str(e)}', type='negative')

                async def delete_role(role_id: int):
                    """Delete a role."""
                    try:
                        async with AsyncSessionLocal() as session:
                            service = RoleService(session)
                            await service.delete_role(role_id)
                        ui.notify('Rol eliminado', type='info')
                        await load_roles()
                    except Exception as e:
                        ui.notify(f'Error al eliminar: {str(e)}', type='negative')

                async def load_roles():
                    """Load and display all roles."""
                    roles_container.clear()
                    
                    async with AsyncSessionLocal() as session:
                        service = RoleService(session)
                        roles = await service.get_all_roles()

                    if not roles:
                        with roles_container:
                            ui.label('No hay roles definidos.').classes('text-gray-500 italic')
                        return

                    with roles_container:
                        # Define system roles
                        SYSTEM_ROLES = ['Administrador', 'Manager', 'Vendedor', 'Viewer']

                        for role in roles:
                            is_system_role = role.name in SYSTEM_ROLES

                            with ui.card().classes('w-full'):
                                with ui.row().classes('w-full items-center justify-between'):
                                    # Role Info
                                    with ui.column().classes('gap-1'):
                                        with ui.row().classes('items-center gap-2'):
                                            ui.icon('badge', color='primary')
                                            ui.label(role.name).classes('text-lg font-bold')
                                            # Add system badge if it's a system role
                                            if is_system_role:
                                                ui.chip('Sistema', icon='lock').props('dense color=accent size=sm')
                                        if role.description:
                                            ui.label(role.description).classes('text-gray-600 text-sm ml-8')

                                    # Permissions Count Chip
                                    perm_count = len(role.permissions)
                                    ui.chip(f'{perm_count} Permisos', icon='vpn_key').classes('bg-blue-50 text-blue-800')

                                    # Actions
                                    with ui.row():
                                        # Edit button - always enabled
                                        edit_btn = ui.button(icon='edit', on_click=lambda r=role: show_role_dialog(r)).props('flat round color=primary')
                                        if is_system_role:
                                            edit_btn.tooltip('Editar permisos del rol (el nombre no se puede cambiar)')
                                        else:
                                            edit_btn.tooltip('Editar rol')

                                        # Delete button - disabled for system roles
                                        if not is_system_role:
                                            ui.button(icon='delete', on_click=lambda r=role: delete_role(r.id)).props('flat round color=negative').tooltip('Eliminar rol')
                                        else:
                                            # Show a disabled delete button with tooltip for system roles
                                            ui.button(icon='delete').props('flat round disabled').tooltip('Los roles del sistema no se pueden eliminar')
                                
                                # Permissions Detail (Expandable)
                                with ui.expansion('Ver permisos asignados').classes('w-full text-sm text-gray-500'):
                                    if not role.permissions:
                                        ui.label('Sin permisos asignados').classes('text-gray-400 italic p-2')
                                    else:
                                        with ui.row().classes('gap-2 p-2 flex-wrap'):
                                            for p in role.permissions:
                                                ui.chip(f"{p.resource}:{p.action}", icon='check_circle').props('dense outline color=secondary')

                # Initial Load
                await load_roles()
