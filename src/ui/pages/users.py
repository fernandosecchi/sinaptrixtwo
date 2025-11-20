"""Users management page with full CRUD operations."""
from datetime import datetime
from typing import Optional
from nicegui import ui
from sqlalchemy import select, delete, update
from src.database import AsyncSessionLocal
from src.models.users.user import User
from src.services.users.user_service import UserService
from src.services.auth.role_service import RoleService
from src.ui.layouts import theme_layout


def create_users_page():
    """Register the users page route with complete CRUD functionality."""
    
    @ui.page("/usuarios")
    async def usuarios_page():
        with theme_layout('Gestión de Usuarios'):
            with ui.column().classes('w-full max-w-7xl gap-4'):
                # Header with title and add button
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label('Usuarios del Sistema').classes('text-3xl font-bold text-primary')
                    ui.button('Nuevo Usuario', on_click=lambda: show_user_dialog(), icon='person_add').props('color=primary')
                
                # Search bar
                with ui.row().classes('w-full gap-4 items-center'):
                    search_input = ui.input('Buscar usuarios...').props('outlined dense clearable').classes('flex-1')

                    async def perform_search():
                        await load_users()

                    # Search button
                    ui.button('Buscar', on_click=perform_search, icon='search').props('color=primary')

                    # Clear button
                    async def clear_search():
                        search_input.value = ''
                        await load_users()

                    ui.button('Limpiar', on_click=clear_search, icon='clear').props('flat')

                    # Also search on Enter key
                    search_input.on('keydown.enter', perform_search)

                    # Switch to show deleted users
                    show_deleted_switch = ui.switch('Mostrar desactivados', on_change=load_users)
                
                # Users table container
                table_container = ui.column().classes('w-full')
                
                # User dialog for add/edit
                user_dialog = ui.dialog()
                with user_dialog, ui.card().classes('w-96'):
                    dialog_title = ui.label('').classes('text-xl font-semibold')
                    
                    # Form inputs
                    ui.separator()
                    with ui.column().classes('w-full gap-4 mt-4'):
                        first_name_input = ui.input('Nombre *').props('outlined dense').classes('w-full')
                        last_name_input = ui.input('Apellido *').props('outlined dense').classes('w-full')
                        email_input = ui.input('Email *').props('outlined dense type=email').classes('w-full')
                        
                        # Hidden field to store user ID for editing
                        user_id_input = ui.input().props('hidden')
                    
                    # Dialog actions
                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancelar', on_click=user_dialog.close).props('flat')
                        
                        async def save_user():
                            # Validation
                            if not first_name_input.value or not last_name_input.value or not email_input.value:
                                ui.notify('Todos los campos marcados con * son requeridos', type='warning')
                                return
                            
                            try:
                                async with AsyncSessionLocal() as session:
                                    user_service = UserService(session)
                                    if user_id_input.value:  # Edit mode
                                        await user_service.update_user(
                                            user_id=int(user_id_input.value),
                                            first_name=first_name_input.value,
                                            last_name=last_name_input.value,
                                            email=email_input.value
                                        )
                                        ui.notify(f'Usuario actualizado exitosamente', type='positive')
                                    else:  # Add mode
                                        await user_service.create_user(
                                            first_name=first_name_input.value,
                                            last_name=last_name_input.value,
                                            email=email_input.value
                                        )
                                        ui.notify(f'Usuario {first_name_input.value} {last_name_input.value} creado', type='positive')
                                
                                # Clear form and close dialog
                                clear_form()
                                user_dialog.close()
                                await load_users()
                                
                            except ValueError as e:
                                ui.notify(str(e), type='negative')
                            except Exception as e:
                                ui.notify(f'Error: {str(e)}', type='negative')
                        
                        save_button = ui.button('Guardar', on_click=save_user).props('color=primary')
                
                # Role Assignment Dialog
                roles_dialog = ui.dialog()
                with roles_dialog, ui.card().classes('w-96'):
                    ui.label('Asignar Roles').classes('text-xl font-semibold')
                    roles_dialog_user_id = ui.input().props('hidden')
                    roles_container = ui.column().classes('w-full gap-2 mt-4')
                    
                    async def save_roles():
                        user_id = int(roles_dialog_user_id.value)
                        # Collect selected roles from checkboxes
                        selected_roles = [role_name for role_name, cb in roles_checkboxes.items() if cb.value]
                        
                        try:
                            async with AsyncSessionLocal() as session:
                                user_service = UserService(session)
                                # First remove all roles (simplified approach)
                                # In a real scenario, you might want a bulk update method or smart diff
                                user = await user_service.get_user(user_id)
                                current_roles = [r.name for r in user.roles]
                                
                                # Add new roles
                                for role in selected_roles:
                                    if role not in current_roles:
                                        await user_service.assign_role(user_id, role)
                                
                                # Remove unselected roles
                                for role in current_roles:
                                    if role not in selected_roles:
                                        await user_service.remove_role(user_id, role)
                                        
                            ui.notify('Roles actualizados', type='positive')
                            roles_dialog.close()
                            await load_users()
                        except Exception as e:
                            ui.notify(f'Error: {str(e)}', type='negative')

                    with ui.row().classes('w-full justify-end mt-4'):
                        ui.button('Cancelar', on_click=roles_dialog.close).props('flat')
                        ui.button('Guardar', on_click=save_roles).props('color=primary')
                
                roles_checkboxes = {}

                async def show_roles_dialog(user):
                    roles_dialog_user_id.value = str(user['id'])
                    roles_container.clear()
                    roles_checkboxes.clear()
                    
                    # Load all available roles and user's current roles
                    async with AsyncSessionLocal() as session:
                        role_service = RoleService(session)
                        all_roles = await role_service.get_all_roles()
                        
                        user_service = UserService(session)
                        # We need to fetch user again to ensure roles are loaded if not present in list view
                        db_user = await user_service.get_user(user['id'])
                        user_role_names = [r.name for r in db_user.roles]

                    with roles_container:
                        if not all_roles:
                            ui.label('No hay roles configurados en el sistema').classes('italic text-gray-500')
                        
                        for role in all_roles:
                            cb = ui.checkbox(role.name, value=role.name in user_role_names)
                            roles_checkboxes[role.name] = cb

                    roles_dialog.open()

                # View details dialog
                details_dialog = ui.dialog()
                with details_dialog, ui.card().classes('w-96'):
                    ui.label('Detalles del Usuario').classes('text-xl font-semibold')
                    ui.separator()
                    details_container = ui.column().classes('w-full gap-3 mt-4')
                    
                    with ui.row().classes('w-full justify-end mt-4'):
                        ui.button('Cerrar', on_click=details_dialog.close).props('color=primary')
                
                # Delete confirmation dialog
                delete_dialog = ui.dialog()
                with delete_dialog, ui.card():
                    ui.label('¿Confirmar desactivación?').classes('text-lg font-semibold')
                    delete_message = ui.label('').classes('mt-2')
                    
                    with ui.row().classes('gap-2 mt-4'):
                        ui.button('Cancelar', on_click=delete_dialog.close).props('flat')
                        
                        async def confirm_delete():
                            user_id = delete_dialog.user_id
                            try:
                                async with AsyncSessionLocal() as session:
                                    user_service = UserService(session)
                                    await user_service.delete_user(user_id)
                                ui.notify('Usuario desactivado exitosamente', type='info')
                                delete_dialog.close()
                                await load_users()
                            except Exception as e:
                                ui.notify(f'Error al desactivar: {str(e)}', type='negative')
                        
                        ui.button('Desactivar', on_click=confirm_delete).props('color=negative')

                # Restore confirmation dialog
                restore_dialog = ui.dialog()
                with restore_dialog, ui.card():
                    ui.label('¿Confirmar restauración?').classes('text-lg font-semibold')
                    restore_message = ui.label('').classes('mt-2')
                    
                    with ui.row().classes('gap-2 mt-4'):
                        ui.button('Cancelar', on_click=restore_dialog.close).props('flat')
                        
                        async def confirm_restore():
                            user_id = restore_dialog.user_id
                            try:
                                async with AsyncSessionLocal() as session:
                                    user_service = UserService(session)
                                    await user_service.restore_user(user_id)
                                ui.notify('Usuario restaurado exitosamente', type='positive')
                                restore_dialog.close()
                                await load_users()
                            except Exception as e:
                                ui.notify(f'Error al restaurar: {str(e)}', type='negative')
                        
                        ui.button('Restaurar', on_click=confirm_restore).props('color=positive')
                
                def clear_form():
                    """Clear all form inputs."""
                    first_name_input.value = ''
                    last_name_input.value = ''
                    email_input.value = ''
                    user_id_input.value = ''
                
                def show_user_dialog(user=None):
                    """Show the user dialog for adding or editing."""
                    clear_form()
                    if user:
                        # Edit mode
                        dialog_title.text = 'Editar Usuario'
                        user_id_input.value = str(user['id'])
                        first_name_input.value = user['first_name']
                        last_name_input.value = user['last_name']
                        email_input.value = user['email']
                    else:
                        # Add mode
                        dialog_title.text = 'Nuevo Usuario'
                    user_dialog.open()
                
                def show_details(user):
                    """Show user details in a dialog."""
                    details_container.clear()
                    with details_container:
                        # ID and Name
                        with ui.row().classes('w-full gap-2'):
                            ui.label('ID:').classes('font-bold')
                            ui.label(str(user['id']))
                        
                        with ui.row().classes('w-full gap-2'):
                            ui.label('Nombre completo:').classes('font-bold')
                            ui.label(f"{user['first_name']} {user['last_name']}")
                        
                        with ui.row().classes('w-full gap-2'):
                            ui.label('Email:').classes('font-bold')
                            ui.label(user['email'])
                        
                        with ui.row().classes('w-full gap-2'):
                            ui.label('Fecha de registro:').classes('font-bold')
                            ui.label(user['created_at'])
                        
                        # Display roles
                        with ui.row().classes('w-full gap-2 items-start'):
                            ui.label('Roles:').classes('font-bold')
                            if user.get('roles'):
                                with ui.row().classes('gap-1'):
                                    for role_name in user['roles']:
                                        ui.chip(role_name, icon='badge').props('dense square color=secondary text-color=white')
                            else:
                                ui.label('Sin roles').classes('text-gray-400 italic')
                    
                    details_dialog.open()
                
                def show_delete_confirmation(user):
                    """Show delete confirmation dialog."""
                    delete_dialog.user_id = user['id']
                    delete_message.text = f"¿Estás seguro de que deseas desactivar al usuario {user['first_name']} {user['last_name']}?"
                    delete_dialog.open()

                def show_restore_confirmation(user):
                    """Show restore confirmation dialog."""
                    restore_dialog.user_id = user['id']
                    restore_message.text = f"¿Estás seguro de que deseas restaurar al usuario {user['full_name']}?"
                    restore_dialog.open()
                
                async def load_users():
                    """Load and display users in the table."""
                    table_container.clear()
                    
                    try:
                        async with AsyncSessionLocal() as session:
                            user_service = UserService(session)
                            search_term = search_input.value
                            include_deleted = show_deleted_switch.value
                            
                            if search_term:
                                users = await user_service.search_users(search_term, include_deleted)
                            else:
                                if include_deleted:
                                    users = await user_service.get_deleted_users()
                                else:
                                    users = await user_service.get_all_users()
                        
                        if not users:
                            with table_container:
                                with ui.card().classes('w-full p-8 text-center'):
                                    ui.icon('person_off', size='xl').classes('text-gray-400')
                                    ui.label('No se encontraron usuarios').classes('text-gray-500 text-lg mt-2')
                                    if search_input.value:
                                        ui.label('Intenta con otros términos de búsqueda').classes('text-gray-400 text-sm')
                        else:
                            with table_container:
                                # Stats card
                                with ui.card().classes('w-full p-4 mb-4'):
                                    with ui.row().classes('gap-8'):
                                        count = len(users)
                                        status_label = "desactivados" if show_deleted_switch.value else "activos"
                                        ui.label(f'Total de usuarios {status_label}: {count}').classes('text-lg')
                                        if search_input.value:
                                            ui.label(f'Resultados filtrados').classes('text-sm text-gray-500')
                                
                                # Users table
                                columns = [
                                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'left'},
                                    {'name': 'full_name', 'label': 'Nombre Completo', 'field': 'full_name', 'sortable': True, 'align': 'left'},
                                    {'name': 'email', 'label': 'Email', 'field': 'email', 'sortable': True, 'align': 'left'},
                                    {'name': 'status', 'label': 'Estado', 'field': 'status', 'sortable': True, 'align': 'center'},
                                    {'name': 'roles', 'label': 'Roles', 'field': 'roles_display', 'align': 'left'},
                                    {'name': 'created_at', 'label': 'Fecha Registro', 'field': 'created_at', 'sortable': True, 'align': 'left'},
                                    {'name': 'actions', 'label': 'Acciones', 'field': 'actions', 'align': 'center'},
                                ]
                                
                                rows = []
                                for user in users:
                                    # Extract role names safely
                                    role_names = [r.name for r in user.roles] if user.roles else []
                                    rows.append({
                                        'id': user.id,
                                        'full_name': user.full_name,
                                        'first_name': user.first_name,
                                        'last_name': user.last_name,
                                        'email': user.email,
                                        'status': 'Desactivado' if user.is_deleted else 'Activo',
                                        'created_at': user.created_at.strftime('%d/%m/%Y %H:%M'),
                                        'is_deleted': user.is_deleted,
                                        'roles': role_names,
                                        'roles_display': ', '.join(role_names) if role_names else '-'
                                    })
                                
                                table = ui.table(
                                    columns=columns,
                                    rows=rows,
                                    row_key='id',
                                    title='Lista de Usuarios',
                                    pagination={'rowsPerPage': 10, 'sortBy': 'created_at', 'descending': True}
                                ).classes('w-full')
                                
                                # Custom actions slot with dynamic buttons
                                table.add_slot('body-cell-actions', r'''
                                    <q-td :props="props" class="text-center">
                                        <q-btn @click="$parent.$emit('roles', props.row)" icon="admin_panel_settings" 
                                               color="accent" flat dense round size="sm">
                                            <q-tooltip>Asignar Roles</q-tooltip>
                                        </q-btn>
                                        <q-btn @click="$parent.$emit('view', props.row)" icon="visibility" 
                                               color="info" flat dense round size="sm" class="q-ml-sm">
                                            <q-tooltip>Ver detalles</q-tooltip>
                                        </q-btn>
                                        <q-btn v-if="!props.row.is_deleted" 
                                               @click="$parent.$emit('edit', props.row)" icon="edit" 
                                               color="warning" flat dense round size="sm" class="q-ml-sm">
                                            <q-tooltip>Editar</q-tooltip>
                                        </q-btn>
                                        <q-btn v-if="!props.row.is_deleted" 
                                               @click="$parent.$emit('delete', props.row)" icon="toggle_off" 
                                               color="negative" flat dense round size="sm" class="q-ml-sm">
                                            <q-tooltip>Desactivar</q-tooltip>
                                        </q-btn>
                                        <q-btn v-if="props.row.is_deleted" 
                                               @click="$parent.$emit('restore', props.row)" icon="toggle_on" 
                                               color="positive" flat dense round size="sm" class="q-ml-sm">
                                            <q-tooltip>Restaurar</q-tooltip>
                                        </q-btn>
                                    </q-td>
                                ''')
                                
                                # Event handlers
                                table.on('view', lambda e: show_details(e.args))
                                table.on('edit', lambda e: show_user_dialog(e.args))
                                table.on('roles', lambda e: show_roles_dialog(e.args))
                                table.on('delete', lambda e: show_delete_confirmation(e.args))
                                table.on('restore', lambda e: show_restore_confirmation(e.args))
                    
                    except Exception as e:
                        with table_container:
                            with ui.card().classes('w-full p-4 bg-red-50'):
                                ui.label(f'Error al cargar usuarios: {str(e)}').classes('text-red-600')
                
                # Load users initially
                await load_users()
                
                # Footer with refresh button
                with ui.row().classes('w-full justify-between mt-4'):
                    ui.label('Última actualización: ' + datetime.now().strftime('%H:%M:%S')).classes('text-gray-500')
                    ui.button('Actualizar', on_click=load_users, icon='refresh').props('flat color=primary')