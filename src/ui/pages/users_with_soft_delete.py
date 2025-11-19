"""Users management page with soft delete support."""
from datetime import datetime
from typing import Optional
from nicegui import ui
from src.database import AsyncSessionLocal
from src.services.user_service import UserService
from src.ui.layouts import theme_layout


def create_users_page():
    """Register the users page route with soft delete functionality."""
    
    @ui.page("/usuarios")
    async def usuarios_page():
        with theme_layout('Gestión de Usuarios'):
            with ui.column().classes('w-full max-w-7xl gap-4'):
                # State management using a dictionary to store state
                state = {'show_deleted': False}
                
                # Header with title and add button
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label('Usuarios del Sistema').classes('text-3xl font-bold text-primary')
                    with ui.row().classes('gap-2'):
                        deleted_switch = ui.switch('Mostrar eliminados')
                        deleted_switch.on_value_change(lambda e: toggle_deleted_view(e.value))
                        ui.button('Nuevo Usuario', on_click=lambda: show_user_dialog(), icon='person_add').props('color=primary')
                
                # Search bar
                with ui.row().classes('w-full gap-4'):
                    search_input = ui.input('Buscar usuarios...').props('outlined dense clearable').classes('flex-1')
                    search_input.on('input', lambda: load_users())
                
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
                                    service = UserService(session)
                                    
                                    if user_id_input.value:  # Edit mode
                                        user = await service.update_user(
                                            int(user_id_input.value),
                                            first_name=first_name_input.value,
                                            last_name=last_name_input.value,
                                            email=email_input.value
                                        )
                                        if user:
                                            ui.notify(f'Usuario actualizado exitosamente', type='positive')
                                        else:
                                            ui.notify('Error al actualizar usuario', type='negative')
                                    else:  # Add mode
                                        user = await service.create_user(
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
                    ui.label('¿Confirmar eliminación?').classes('text-lg font-semibold')
                    delete_message = ui.label('').classes('mt-2')
                    delete_type = {'value': 'soft'}  # 'soft' or 'hard'
                    
                    with ui.row().classes('gap-2 mt-4'):
                        ui.button('Cancelar', on_click=delete_dialog.close).props('flat')
                        
                        async def confirm_delete():
                            user_id = delete_dialog.user_id
                            try:
                                async with AsyncSessionLocal() as session:
                                    service = UserService(session)
                                    
                                    if delete_type['value'] == 'hard':
                                        success = await service.hard_delete_user(user_id)
                                        message = 'Usuario eliminado permanentemente'
                                    else:
                                        success = await service.delete_user(user_id)
                                        message = 'Usuario eliminado exitosamente'
                                    
                                    if success:
                                        ui.notify(message, type='info')
                                    else:
                                        ui.notify('Error al eliminar usuario', type='negative')
                                    
                                delete_dialog.close()
                                await load_users()
                            except Exception as e:
                                ui.notify(f'Error al eliminar: {str(e)}', type='negative')
                        
                        delete_button = ui.button('Eliminar', on_click=confirm_delete).props('color=negative')
                
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
                        user_id_input.value = str(user.id)
                        first_name_input.value = user.first_name
                        last_name_input.value = user.last_name
                        email_input.value = user.email
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
                            ui.label(str(user.id))
                        
                        with ui.row().classes('w-full gap-2'):
                            ui.label('Nombre completo:').classes('font-bold')
                            ui.label(f"{user.first_name} {user.last_name}")
                        
                        with ui.row().classes('w-full gap-2'):
                            ui.label('Email:').classes('font-bold')
                            ui.label(user.email)
                        
                        with ui.row().classes('w-full gap-2'):
                            ui.label('Fecha de registro:').classes('font-bold')
                            ui.label(user.created_at.strftime('%d/%m/%Y %H:%M'))
                        
                        if user.updated_at:
                            with ui.row().classes('w-full gap-2'):
                                ui.label('Última modificación:').classes('font-bold')
                                ui.label(user.updated_at.strftime('%d/%m/%Y %H:%M'))
                        
                        if user.deleted_at:
                            with ui.row().classes('w-full gap-2'):
                                ui.label('Fecha de eliminación:').classes('font-bold')
                                ui.label(user.deleted_at.strftime('%d/%m/%Y %H:%M'))
                        
                        with ui.row().classes('w-full gap-2'):
                            ui.label('Estado:').classes('font-bold')
                            if user.is_deleted:
                                ui.label('Eliminado').classes('text-red-500')
                            else:
                                ui.label('Activo').classes('text-green-500')
                    
                    details_dialog.open()
                
                def show_delete_confirmation(user, hard=False):
                    """Show delete confirmation dialog."""
                    delete_dialog.user_id = user.id
                    delete_type['value'] = 'hard' if hard else 'soft'
                    
                    if hard:
                        delete_message.text = f"¿Estás seguro de que deseas eliminar PERMANENTEMENTE al usuario {user.first_name} {user.last_name}? Esta acción no se puede deshacer."
                        delete_button.text = 'Eliminar Permanentemente'
                        delete_button.props('color=negative')
                    else:
                        delete_message.text = f"¿Estás seguro de que deseas eliminar al usuario {user.first_name} {user.last_name}?"
                        delete_button.text = 'Eliminar'
                        delete_button.props('color=warning')
                    
                    delete_dialog.open()
                
                async def restore_user(user_id):
                    """Restore a soft-deleted user."""
                    try:
                        async with AsyncSessionLocal() as session:
                            service = UserService(session)
                            success = await service.restore_user(user_id)
                            if success:
                                ui.notify('Usuario restaurado exitosamente', type='positive')
                                await load_users()
                            else:
                                ui.notify('Error al restaurar usuario', type='negative')
                    except Exception as e:
                        ui.notify(f'Error: {str(e)}', type='negative')
                
                async def load_users():
                    """Load and display users in the table."""
                    table_container.clear()
                    
                    try:
                        async with AsyncSessionLocal() as session:
                            service = UserService(session)
                            
                            # Get users based on current view mode
                            if state['show_deleted']:
                                users = await service.get_deleted_users()
                                title_text = 'Usuarios Eliminados'
                            else:
                                if search_input.value:
                                    users = await service.search_users(search_input.value, include_deleted=False)
                                else:
                                    users = await service.get_all_users(include_deleted=False)
                                title_text = 'Usuarios Activos'
                        
                        if not users:
                            with table_container:
                                with ui.card().classes('w-full p-8 text-center'):
                                    ui.icon('person_off', size='xl').classes('text-gray-400')
                                    if state['show_deleted']:
                                        ui.label('No hay usuarios eliminados').classes('text-gray-500 text-lg mt-2')
                                    else:
                                        ui.label('No se encontraron usuarios').classes('text-gray-500 text-lg mt-2')
                                        if search_input.value:
                                            ui.label('Intenta con otros términos de búsqueda').classes('text-gray-400 text-sm')
                        else:
                            with table_container:
                                # Stats card
                                with ui.card().classes('w-full p-4 mb-4'):
                                    with ui.row().classes('gap-8'):
                                        ui.label(f'{title_text}: {len(users)}').classes('text-lg')
                                        if search_input.value and not state['show_deleted']:
                                            ui.label(f'Resultados filtrados').classes('text-sm text-gray-500')
                                
                                # Users table
                                columns = [
                                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'left'},
                                    {'name': 'first_name', 'label': 'Nombre', 'field': 'first_name', 'sortable': True, 'align': 'left'},
                                    {'name': 'last_name', 'label': 'Apellido', 'field': 'last_name', 'sortable': True, 'align': 'left'},
                                    {'name': 'email', 'label': 'Email', 'field': 'email', 'sortable': True, 'align': 'left'},
                                ]
                                
                                if state['show_deleted']:
                                    columns.append({'name': 'deleted_at', 'label': 'Fecha Eliminación', 'field': 'deleted_at', 'sortable': True, 'align': 'left'})
                                else:
                                    columns.append({'name': 'created_at', 'label': 'Fecha Registro', 'field': 'created_at', 'sortable': True, 'align': 'left'})
                                
                                columns.append({'name': 'actions', 'label': 'Acciones', 'field': 'actions', 'align': 'center'})
                                
                                rows = []
                                for user in users:
                                    row = {
                                        'id': user.id,
                                        'first_name': user.first_name,
                                        'last_name': user.last_name,
                                        'email': user.email,
                                    }
                                    
                                    if state['show_deleted'] and user.deleted_at:
                                        row['deleted_at'] = user.deleted_at.strftime('%d/%m/%Y %H:%M')
                                    else:
                                        row['created_at'] = user.created_at.strftime('%d/%m/%Y %H:%M')
                                    
                                    rows.append(row)
                                
                                table = ui.table(
                                    columns=columns,
                                    rows=rows,
                                    row_key='id',
                                    title=title_text,
                                    pagination={'rowsPerPage': 10, 'sortBy': 'deleted_at' if state['show_deleted'] else 'created_at', 'descending': True}
                                ).classes('w-full')
                                
                                # Custom actions slot based on view mode
                                if state['show_deleted']:
                                    # Actions for deleted users: view, restore, permanent delete
                                    table.add_slot('body-cell-actions', r'''
                                        <q-td :props="props" class="text-center">
                                            <q-btn @click="$parent.$emit('view', props.row)" icon="visibility" 
                                                   color="info" flat dense round size="sm">
                                                <q-tooltip>Ver detalles</q-tooltip>
                                            </q-btn>
                                            <q-btn @click="$parent.$emit('restore', props.row)" icon="restore" 
                                                   color="positive" flat dense round size="sm" class="q-ml-sm">
                                                <q-tooltip>Restaurar</q-tooltip>
                                            </q-btn>
                                            <q-btn @click="$parent.$emit('hard_delete', props.row)" icon="delete_forever" 
                                                   color="negative" flat dense round size="sm" class="q-ml-sm">
                                                <q-tooltip>Eliminar permanentemente</q-tooltip>
                                            </q-btn>
                                        </q-td>
                                    ''')
                                    
                                    # Event handlers for deleted users
                                    table.on('view', lambda e: show_details(next(u for u in users if u.id == e.args['id'])))
                                    table.on('restore', lambda e: restore_user(e.args['id']))
                                    table.on('hard_delete', lambda e: show_delete_confirmation(
                                        next(u for u in users if u.id == e.args['id']), hard=True
                                    ))
                                else:
                                    # Actions for active users: view, edit, soft delete
                                    table.add_slot('body-cell-actions', r'''
                                        <q-td :props="props" class="text-center">
                                            <q-btn @click="$parent.$emit('view', props.row)" icon="visibility" 
                                                   color="info" flat dense round size="sm">
                                                <q-tooltip>Ver detalles</q-tooltip>
                                            </q-btn>
                                            <q-btn @click="$parent.$emit('edit', props.row)" icon="edit" 
                                                   color="warning" flat dense round size="sm" class="q-ml-sm">
                                                <q-tooltip>Editar</q-tooltip>
                                            </q-btn>
                                            <q-btn @click="$parent.$emit('delete', props.row)" icon="delete" 
                                                   color="negative" flat dense round size="sm" class="q-ml-sm">
                                                <q-tooltip>Eliminar</q-tooltip>
                                            </q-btn>
                                        </q-td>
                                    ''')
                                    
                                    # Event handlers for active users
                                    table.on('view', lambda e: show_details(next(u for u in users if u.id == e.args['id'])))
                                    table.on('edit', lambda e: show_user_dialog(next(u for u in users if u.id == e.args['id'])))
                                    table.on('delete', lambda e: show_delete_confirmation(
                                        next(u for u in users if u.id == e.args['id']), hard=False
                                    ))
                    
                    except Exception as e:
                        with table_container:
                            with ui.card().classes('w-full p-4 bg-red-50'):
                                ui.label(f'Error al cargar usuarios: {str(e)}').classes('text-red-600')
                
                # Load users initially
                await load_users()
                
                # Function to toggle deleted view
                def toggle_deleted_view(value):
                    state['show_deleted'] = value
                    load_users()
                
                # Footer with refresh button
                with ui.row().classes('w-full justify-between mt-4'):
                    ui.label('Última actualización: ' + datetime.now().strftime('%H:%M:%S')).classes('text-gray-500')
                    ui.button('Actualizar', on_click=load_users, icon='refresh').props('flat color=primary')
