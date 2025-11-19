"""Users management page with full CRUD operations."""
from datetime import datetime
from typing import Optional
from nicegui import ui
from sqlalchemy import select, delete, update
from src.database import AsyncSessionLocal
from src.models.user import User
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
                                    if user_id_input.value:  # Edit mode
                                        stmt = (
                                            update(User)
                                            .where(User.id == int(user_id_input.value))
                                            .values(
                                                first_name=first_name_input.value,
                                                last_name=last_name_input.value,
                                                email=email_input.value
                                            )
                                        )
                                        await session.execute(stmt)
                                        await session.commit()
                                        ui.notify(f'Usuario actualizado exitosamente', type='positive')
                                    else:  # Add mode
                                        new_user = User(
                                            first_name=first_name_input.value,
                                            last_name=last_name_input.value,
                                            email=email_input.value
                                        )
                                        session.add(new_user)
                                        await session.commit()
                                        ui.notify(f'Usuario {first_name_input.value} {last_name_input.value} creado', type='positive')
                                
                                # Clear form and close dialog
                                clear_form()
                                user_dialog.close()
                                await load_users()
                                
                            except Exception as e:
                                if 'unique' in str(e).lower():
                                    ui.notify('El email ya está registrado', type='negative')
                                else:
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
                    
                    with ui.row().classes('gap-2 mt-4'):
                        ui.button('Cancelar', on_click=delete_dialog.close).props('flat')
                        
                        async def confirm_delete():
                            user_id = delete_dialog.user_id
                            try:
                                async with AsyncSessionLocal() as session:
                                    await session.execute(delete(User).where(User.id == user_id))
                                    await session.commit()
                                ui.notify('Usuario eliminado exitosamente', type='info')
                                delete_dialog.close()
                                await load_users()
                            except Exception as e:
                                ui.notify(f'Error al eliminar: {str(e)}', type='negative')
                        
                        ui.button('Eliminar', on_click=confirm_delete).props('color=negative')
                
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
                    
                    details_dialog.open()
                
                def show_delete_confirmation(user):
                    """Show delete confirmation dialog."""
                    delete_dialog.user_id = user['id']
                    delete_message.text = f"¿Estás seguro de que deseas eliminar al usuario {user['first_name']} {user['last_name']}?"
                    delete_dialog.open()
                
                async def load_users():
                    """Load and display users in the table."""
                    table_container.clear()
                    
                    try:
                        async with AsyncSessionLocal() as session:
                            query = select(User).order_by(User.created_at.desc())
                            
                            # Apply search filter if present
                            if search_input.value:
                                search_term = f"%{search_input.value}%"
                                query = query.where(
                                    (User.first_name.ilike(search_term)) |
                                    (User.last_name.ilike(search_term)) |
                                    (User.email.ilike(search_term))
                                )
                            
                            result = await session.execute(query)
                            users = result.scalars().all()
                        
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
                                        ui.label(f'Total de usuarios: {len(users)}').classes('text-lg')
                                        if search_input.value:
                                            ui.label(f'Resultados filtrados').classes('text-sm text-gray-500')
                                
                                # Users table
                                columns = [
                                    {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'left'},
                                    {'name': 'first_name', 'label': 'Nombre', 'field': 'first_name', 'sortable': True, 'align': 'left'},
                                    {'name': 'last_name', 'label': 'Apellido', 'field': 'last_name', 'sortable': True, 'align': 'left'},
                                    {'name': 'email', 'label': 'Email', 'field': 'email', 'sortable': True, 'align': 'left'},
                                    {'name': 'created_at', 'label': 'Fecha Registro', 'field': 'created_at', 'sortable': True, 'align': 'left'},
                                    {'name': 'actions', 'label': 'Acciones', 'field': 'actions', 'align': 'center'},
                                ]
                                
                                rows = []
                                for user in users:
                                    rows.append({
                                        'id': user.id,
                                        'first_name': user.first_name,
                                        'last_name': user.last_name,
                                        'email': user.email,
                                        'created_at': user.created_at.strftime('%d/%m/%Y %H:%M'),
                                    })
                                
                                table = ui.table(
                                    columns=columns,
                                    rows=rows,
                                    row_key='id',
                                    title='Lista de Usuarios',
                                    pagination={'rowsPerPage': 10, 'sortBy': 'created_at', 'descending': True}
                                ).classes('w-full')
                                
                                # Custom actions slot with three buttons
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
                                
                                # Event handlers
                                table.on('view', lambda e: show_details(e.args))
                                table.on('edit', lambda e: show_user_dialog(e.args))
                                table.on('delete', lambda e: show_delete_confirmation(e.args))
                    
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