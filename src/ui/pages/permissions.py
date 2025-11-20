"""Permission management page for creating and managing system permissions."""
from datetime import datetime
from typing import List, Dict
from nicegui import ui
from src.database import AsyncSessionLocal
from src.services.auth.permission_service import PermissionService
from src.ui.layouts import theme_layout


def create_permissions_page():
    """Register the permissions management page."""

    @ui.page("/permisos")
    async def permissions_page():
        breadcrumb_items = [
            ('Configuración', '/'),
            ('Permisos', '/permisos')
        ]

        with theme_layout('Gestión de Permisos', breadcrumb_items=breadcrumb_items):
            with ui.column().classes('w-full max-w-7xl gap-4'):
                # Header
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label('Permisos del Sistema').classes('text-3xl font-bold text-primary')
                    ui.button(
                        'Nuevo Permiso',
                        on_click=lambda: show_permission_dialog(),
                        icon='add_task'
                    ).props('color=primary')

                # Stats
                stats_container = ui.row().classes('w-full gap-4 mb-4')

                # Permissions container
                permissions_container = ui.column().classes('w-full gap-4')

                # Permission Dialog
                permission_dialog = ui.dialog()
                with permission_dialog, ui.card().classes('w-[600px]'):
                    dialog_title = ui.label('').classes('text-xl font-semibold mb-4')

                    # Hidden ID for edit mode
                    perm_id_input = ui.input().props('hidden')

                    with ui.column().classes('w-full gap-4'):
                        # Resource and Action inputs with suggestions
                        with ui.row().classes('w-full gap-4'):
                            resource_input = ui.input('Recurso *').props('outlined dense').classes('flex-1')
                            action_input = ui.input('Acción *').props('outlined dense').classes('flex-1')

                        # Auto-generated code display
                        code_display = ui.input('Código (auto-generado)').props('outlined dense filled readonly').classes('w-full')

                        # Name and description
                        name_input = ui.input('Nombre del Permiso *').props('outlined dense').classes('w-full')
                        desc_input = ui.textarea('Descripción').props('outlined dense rows=2').classes('w-full')

                        # Common suggestions
                        ui.label('Sugerencias:').classes('text-sm text-gray-600 mt-2')
                        with ui.row().classes('gap-2 flex-wrap'):
                            ui.chip('Recursos comunes:', icon='category').props('outline')
                            for res in ['customer', 'product', 'order', 'report', 'settings']:
                                ui.chip(
                                    res,
                                    on_click=lambda r=res: resource_input.set_value(r)
                                ).props('clickable outline size=sm')

                        with ui.row().classes('gap-2 flex-wrap'):
                            ui.chip('Acciones comunes:', icon='bolt').props('outline')
                            for act in ['create', 'read', 'update', 'delete', 'export', 'import', 'approve']:
                                ui.chip(
                                    act,
                                    on_click=lambda a=act: action_input.set_value(a)
                                ).props('clickable outline size=sm')

                    # Actions
                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancelar', on_click=permission_dialog.close).props('flat')
                        save_btn = ui.button('Guardar', on_click=lambda: save_permission()).props('color=primary')

                # Update code display when resource or action changes
                def update_code():
                    if resource_input.value and action_input.value:
                        code_display.value = f"{resource_input.value.lower()}:{action_input.value.lower()}"
                    else:
                        code_display.value = ""

                resource_input.on('input', update_code)
                action_input.on('input', update_code)

                def show_permission_dialog(permission=None):
                    """Open dialog for create or edit."""
                    perm_id_input.value = ''
                    resource_input.value = ''
                    action_input.value = ''
                    code_display.value = ''
                    name_input.value = ''
                    desc_input.value = ''

                    if permission:
                        dialog_title.text = 'Editar Permiso'
                        perm_id_input.value = str(permission.id)
                        resource_input.value = permission.resource
                        action_input.value = permission.action
                        code_display.value = permission.code
                        name_input.value = permission.name
                        desc_input.value = permission.description or ''
                        # Disable resource and action for editing
                        resource_input.props('readonly')
                        action_input.props('readonly')
                    else:
                        dialog_title.text = 'Nuevo Permiso'
                        # Enable resource and action for new permission
                        resource_input.props(remove='readonly')
                        action_input.props(remove='readonly')

                    permission_dialog.open()

                async def save_permission():
                    """Save or update permission."""
                    if not resource_input.value or not action_input.value or not name_input.value:
                        ui.notify('Complete todos los campos requeridos', type='warning')
                        return

                    try:
                        async with AsyncSessionLocal() as session:
                            service = PermissionService(session)

                            if perm_id_input.value:  # Edit
                                await service.update_permission(
                                    int(perm_id_input.value),
                                    name=name_input.value,
                                    description=desc_input.value
                                )
                                ui.notify('Permiso actualizado exitosamente', type='positive')
                            else:  # Create
                                await service.create_permission(
                                    code=code_display.value,
                                    name=name_input.value,
                                    resource=resource_input.value.lower(),
                                    action=action_input.value.lower(),
                                    description=desc_input.value
                                )
                                ui.notify('Permiso creado exitosamente', type='positive')

                        permission_dialog.close()
                        await load_permissions()

                    except ValueError as e:
                        ui.notify(str(e), type='warning')
                    except Exception as e:
                        ui.notify(f'Error: {str(e)}', type='negative')

                async def delete_permission(permission_id: int):
                    """Delete a permission."""
                    try:
                        async with AsyncSessionLocal() as session:
                            service = PermissionService(session)
                            await service.delete_permission(permission_id)
                        ui.notify('Permiso eliminado', type='info')
                        await load_permissions()
                    except ValueError as e:
                        ui.notify(str(e), type='warning')
                    except Exception as e:
                        ui.notify(f'Error al eliminar: {str(e)}', type='negative')

                async def load_permissions():
                    """Load and display all permissions grouped by resource."""
                    permissions_container.clear()

                    async with AsyncSessionLocal() as session:
                        service = PermissionService(session)
                        grouped_perms = await service.get_permissions_grouped()
                        all_perms = await service.get_all_permissions()
                        resources = await service.get_available_resources()
                        actions = await service.get_available_actions()

                    # Update stats
                    stats_container.clear()
                    with stats_container:
                        # Total permissions
                        with ui.card().classes('flex-1'):
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('vpn_key', color='primary', size='md')
                                with ui.column().classes('gap-0'):
                                    ui.label(str(len(all_perms))).classes('text-2xl font-bold')
                                    ui.label('Permisos totales').classes('text-sm text-gray-600')

                        # Resources
                        with ui.card().classes('flex-1'):
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('category', color='secondary', size='md')
                                with ui.column().classes('gap-0'):
                                    ui.label(str(len(resources))).classes('text-2xl font-bold')
                                    ui.label('Recursos').classes('text-sm text-gray-600')

                        # Actions
                        with ui.card().classes('flex-1'):
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('bolt', color='accent', size='md')
                                with ui.column().classes('gap-0'):
                                    ui.label(str(len(actions))).classes('text-2xl font-bold')
                                    ui.label('Acciones únicas').classes('text-sm text-gray-600')

                    if not grouped_perms:
                        with permissions_container:
                            ui.label('No hay permisos definidos.').classes('text-gray-500 italic')
                        return

                    # Display permissions grouped by resource
                    with permissions_container:
                        for resource, perms in sorted(grouped_perms.items()):
                            with ui.expansion(
                                f'{resource.upper()} ({len(perms)} permisos)',
                                icon='folder'
                            ).classes('w-full').props('default-opened'):
                                with ui.column().classes('gap-2 p-2'):
                                    for perm in perms:
                                        with ui.card().classes('w-full'):
                                            with ui.row().classes('w-full items-center justify-between'):
                                                # Permission info
                                                with ui.column().classes('gap-1 flex-1'):
                                                    with ui.row().classes('items-center gap-2'):
                                                        ui.icon('key', size='sm', color='primary')
                                                        ui.label(perm.name).classes('font-semibold')
                                                        ui.chip(perm.code, icon='code').props('dense outline color=secondary')
                                                    if perm.description:
                                                        ui.label(perm.description).classes('text-sm text-gray-600 ml-8')

                                                # Actions
                                                with ui.row().classes('gap-1'):
                                                    # Check if it's a system permission
                                                    is_system = perm.code in [
                                                        'dashboard:view',
                                                        'user:read', 'user:create', 'user:update', 'user:delete',
                                                        'role:read', 'role:create', 'role:update', 'role:delete'
                                                    ]

                                                    if is_system:
                                                        ui.chip('Sistema', icon='lock').props('dense color=accent')

                                                    ui.button(
                                                        icon='edit',
                                                        on_click=lambda p=perm: show_permission_dialog(p)
                                                    ).props('flat round color=primary dense')

                                                    # Only allow delete for non-system permissions
                                                    if not is_system:
                                                        ui.button(
                                                            icon='delete',
                                                            on_click=lambda p=perm: delete_permission(p.id)
                                                        ).props('flat round color=negative dense')

                # Initial Load
                await load_permissions()