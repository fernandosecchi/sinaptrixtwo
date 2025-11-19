"""Advanced user search page with filters and enhanced features."""
from datetime import datetime, timedelta
from nicegui import ui
from src.database import AsyncSessionLocal
from src.services.user_search_service import UserSearchService
from src.ui.layouts import theme_layout


def create_advanced_search_page():
    """Register the advanced user search page."""
    
    @ui.page("/usuarios/busqueda")
    async def advanced_search_page():
        with theme_layout('Búsqueda Avanzada de Usuarios'):
            with ui.column().classes('w-full max-w-7xl gap-4'):
                # Page state
                state = {
                    'current_page': 1,
                    'page_size': 20,
                    'sort_by': 'created_at',
                    'sort_desc': True,
                    'filters': {},
                    'search_results': None,
                    'stats': None,
                    'export_format': 'csv'
                }
                
                # Header
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label('Búsqueda Avanzada').classes('text-3xl font-bold text-primary')
                    with ui.row().classes('gap-2'):
                        ui.button(
                            'Volver a Usuarios',
                            icon='arrow_back',
                            on_click=lambda: ui.navigate('/usuarios')
                        ).props('flat')
                        stats_button = ui.button(
                            'Ver Estadísticas',
                            icon='analytics',
                            on_click=lambda: show_stats()
                        ).props('flat')
                
                # Search bar with autocomplete
                with ui.card().classes('w-full p-4'):
                    ui.label('Búsqueda General').classes('text-lg font-semibold mb-2')
                    with ui.row().classes('w-full gap-2'):
                        search_input = ui.input(
                            placeholder='Buscar por nombre, apellido o email...',
                        ).props('outlined dense clearable').classes('flex-1')
                        
                        search_button = ui.button(
                            'Buscar',
                            icon='search',
                            on_click=lambda: perform_search()
                        ).props('color=primary')
                        
                        clear_button = ui.button(
                            'Limpiar',
                            icon='clear',
                            on_click=lambda: clear_search()
                        ).props('flat')
                
                # Advanced filters
                with ui.expansion('Filtros Avanzados', icon='filter_list').classes('w-full'):
                    with ui.card().classes('w-full p-4'):
                        with ui.grid(columns=3).classes('w-full gap-4'):
                            # Field filters
                            first_name_filter = ui.input('Nombre').props('outlined dense')
                            last_name_filter = ui.input('Apellido').props('outlined dense')
                            email_filter = ui.input('Email').props('outlined dense')
                            
                            # Status filter
                            status_filter = ui.select(
                                ['Todos', 'Activos', 'Eliminados'],
                                value='Activos',
                                label='Estado'
                            ).props('outlined dense')
                            
                            # Date filters
                            created_after = ui.input('Creado después de').props('outlined dense type=date')
                            created_before = ui.input('Creado antes de').props('outlined dense type=date')
                            
                            # Quick date ranges
                            date_range = ui.select(
                                [
                                    'Todo el tiempo',
                                    'Hoy',
                                    'Última semana',
                                    'Último mes',
                                    'Últimos 3 meses',
                                    'Último año'
                                ],
                                value='Todo el tiempo',
                                label='Rango rápido'
                            ).props('outlined dense')
                            date_range.on_value_change(lambda e: apply_date_range(e.value))
                        
                        # Apply filters button
                        with ui.row().classes('w-full justify-end mt-4'):
                            ui.button(
                                'Aplicar Filtros',
                                icon='filter_alt',
                                on_click=lambda: apply_filters()
                            ).props('color=primary')
                
                # Sort and display options
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('w-full items-center justify-between'):
                        with ui.row().classes('gap-2 items-center'):
                            ui.label('Ordenar por:')
                            sort_field = ui.select(
                                {
                                    'created_at': 'Fecha de creación',
                                    'updated_at': 'Última modificación',
                                    'first_name': 'Nombre',
                                    'last_name': 'Apellido',
                                    'email': 'Email'
                                },
                                value='created_at'
                            ).props('outlined dense').classes('w-48')
                            
                            sort_order = ui.select(
                                {'desc': 'Descendente', 'asc': 'Ascendente'},
                                value='desc'
                            ).props('outlined dense').classes('w-36')
                            
                            sort_field.on_value_change(lambda e: update_sort('field', e.value))
                            sort_order.on_value_change(lambda e: update_sort('order', e.value))
                        
                        with ui.row().classes('gap-2 items-center'):
                            ui.label('Resultados por página:')
                            page_size_select = ui.select(
                                [10, 20, 50, 100],
                                value=20
                            ).props('outlined dense').classes('w-24')
                            page_size_select.on_value_change(lambda e: update_page_size(e.value))
                
                # Results container
                results_container = ui.column().classes('w-full')
                
                # Export options
                export_dialog = ui.dialog()
                with export_dialog, ui.card().classes('w-96'):
                    ui.label('Exportar Resultados').classes('text-xl font-semibold')
                    ui.separator()
                    
                    with ui.column().classes('w-full gap-4 mt-4'):
                        export_format_select = ui.select(
                            {'csv': 'CSV', 'json': 'JSON'},
                            value='csv',
                            label='Formato'
                        ).props('outlined dense')
                        
                        ui.label('Se exportarán todos los resultados de la búsqueda actual').classes('text-sm text-gray-600')
                    
                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancelar', on_click=export_dialog.close).props('flat')
                        
                        async def download_export():
                            format = export_format_select.value
                            await export_results(format)
                            export_dialog.close()
                        
                        ui.button('Descargar', on_click=download_export).props('color=primary')
                
                # Stats dialog
                stats_dialog = ui.dialog()
                with stats_dialog, ui.card().classes('w-96'):
                    ui.label('Estadísticas de Usuarios').classes('text-xl font-semibold')
                    ui.separator()
                    stats_container = ui.column().classes('w-full gap-4 mt-4')
                    
                    with ui.row().classes('w-full justify-end mt-4'):
                        ui.button('Cerrar', on_click=stats_dialog.close).props('color=primary')
                
                # Functions
                def apply_date_range(range_value):
                    """Apply quick date range selection."""
                    today = datetime.now().date()
                    
                    if range_value == 'Hoy':
                        created_after.value = today.isoformat()
                        created_before.value = today.isoformat()
                    elif range_value == 'Última semana':
                        created_after.value = (today - timedelta(days=7)).isoformat()
                        created_before.value = today.isoformat()
                    elif range_value == 'Último mes':
                        created_after.value = (today - timedelta(days=30)).isoformat()
                        created_before.value = today.isoformat()
                    elif range_value == 'Últimos 3 meses':
                        created_after.value = (today - timedelta(days=90)).isoformat()
                        created_before.value = today.isoformat()
                    elif range_value == 'Último año':
                        created_after.value = (today - timedelta(days=365)).isoformat()
                        created_before.value = today.isoformat()
                    else:  # Todo el tiempo
                        created_after.value = ''
                        created_before.value = ''
                
                def apply_filters():
                    """Apply advanced filters."""
                    state['filters'] = {}
                    
                    # Text filters
                    if first_name_filter.value:
                        state['filters']['first_name'] = first_name_filter.value
                    if last_name_filter.value:
                        state['filters']['last_name'] = last_name_filter.value
                    if email_filter.value:
                        state['filters']['email'] = email_filter.value
                    
                    # Status filter
                    if status_filter.value == 'Eliminados':
                        state['filters']['status'] = 'deleted'
                    elif status_filter.value == 'Todos':
                        state['filters']['status'] = 'all'
                    # Default is active only
                    
                    # Date filters
                    if created_after.value:
                        state['filters']['created_after'] = created_after.value
                    if created_before.value:
                        state['filters']['created_before'] = created_before.value
                    
                    state['current_page'] = 1
                    perform_search()
                
                def update_sort(field, value):
                    """Update sort options."""
                    if field == 'field':
                        state['sort_by'] = value
                    elif field == 'order':
                        state['sort_desc'] = value == 'desc'
                    perform_search()
                
                def update_page_size(value):
                    """Update page size."""
                    state['page_size'] = value
                    state['current_page'] = 1
                    perform_search()
                
                async def perform_search():
                    """Perform search with current parameters."""
                    results_container.clear()
                    
                    try:
                        async with AsyncSessionLocal() as session:
                            search_service = UserSearchService(session)
                            
                            result = await search_service.search(
                                query=search_input.value,
                                filters=state['filters'],
                                page=state['current_page'],
                                page_size=state['page_size'],
                                sort_by=state['sort_by'],
                                sort_desc=state['sort_desc']
                            )
                            
                            state['search_results'] = result
                            display_results(result)
                    
                    except Exception as e:
                        with results_container:
                            with ui.card().classes('w-full p-4 bg-red-50'):
                                ui.label(f'Error en la búsqueda: {str(e)}').classes('text-red-600')
                
                def display_results(result):
                    """Display search results."""
                    with results_container:
                        # Results summary
                        with ui.card().classes('w-full p-4 mb-4'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.row().classes('gap-4'):
                                    ui.label(f"Total: {result['pagination']['total']} usuarios").classes('text-lg')
                                    if result['query']:
                                        ui.label(f"Búsqueda: '{result['query']}'").classes('text-sm text-gray-600')
                                    if result['filters']:
                                        ui.label(f"Filtros aplicados: {len(result['filters'])}").classes('text-sm text-gray-600')
                                
                                ui.button(
                                    'Exportar',
                                    icon='download',
                                    on_click=export_dialog.open
                                ).props('flat')
                        
                        # Results table
                        if result['users']:
                            columns = [
                                {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                                {'name': 'full_name', 'label': 'Nombre Completo', 'field': 'full_name', 'align': 'left'},
                                {'name': 'email', 'label': 'Email', 'field': 'email', 'align': 'left'},
                                {'name': 'status', 'label': 'Estado', 'field': 'status', 'align': 'center'},
                                {'name': 'created_at', 'label': 'Creado', 'field': 'created_at', 'align': 'left'},
                                {'name': 'actions', 'label': 'Acciones', 'field': 'actions', 'align': 'center'},
                            ]
                            
                            rows = []
                            for user in result['users']:
                                rows.append({
                                    'id': user['id'],
                                    'full_name': user['full_name'],
                                    'email': user['email'],
                                    'status': '🔴 Eliminado' if user['is_deleted'] else '🟢 Activo',
                                    'created_at': datetime.fromisoformat(user['created_at']).strftime('%d/%m/%Y %H:%M')
                                })
                            
                            table = ui.table(
                                columns=columns,
                                rows=rows,
                                row_key='id'
                            ).classes('w-full')
                            
                            # Add action buttons
                            table.add_slot('body-cell-actions', r'''
                                <q-td :props="props" class="text-center">
                                    <q-btn @click="$parent.$emit('view', props.row)" 
                                           icon="visibility" flat dense round size="sm" color="info">
                                        <q-tooltip>Ver detalles</q-tooltip>
                                    </q-btn>
                                </q-td>
                            ''')
                            
                            table.on('view', lambda e: ui.navigate(f"/usuarios?id={e.args['id']}"))
                        else:
                            with ui.card().classes('w-full p-8 text-center'):
                                ui.icon('search_off', size='xl').classes('text-gray-400')
                                ui.label('No se encontraron resultados').classes('text-gray-500 text-lg mt-2')
                                if result['query'] or result['filters']:
                                    ui.label('Intenta ajustar los criterios de búsqueda').classes('text-gray-400 text-sm')
                        
                        # Pagination
                        if result['pagination']['pages'] > 1:
                            with ui.card().classes('w-full p-4'):
                                with ui.row().classes('w-full items-center justify-center gap-2'):
                                    ui.button(
                                        icon='first_page',
                                        on_click=lambda: go_to_page(1)
                                    ).props('flat dense round').set_enabled(state['current_page'] > 1)
                                    
                                    ui.button(
                                        icon='chevron_left',
                                        on_click=lambda: go_to_page(state['current_page'] - 1)
                                    ).props('flat dense round').set_enabled(result['pagination']['has_prev'])
                                    
                                    ui.label(
                                        f"Página {result['pagination']['page']} de {result['pagination']['pages']}"
                                    ).classes('mx-4')
                                    
                                    ui.button(
                                        icon='chevron_right',
                                        on_click=lambda: go_to_page(state['current_page'] + 1)
                                    ).props('flat dense round').set_enabled(result['pagination']['has_next'])
                                    
                                    ui.button(
                                        icon='last_page',
                                        on_click=lambda: go_to_page(result['pagination']['pages'])
                                    ).props('flat dense round').set_enabled(
                                        state['current_page'] < result['pagination']['pages']
                                    )
                
                def go_to_page(page):
                    """Navigate to specific page."""
                    state['current_page'] = page
                    perform_search()
                
                def clear_search():
                    """Clear all search parameters."""
                    search_input.value = ''
                    first_name_filter.value = ''
                    last_name_filter.value = ''
                    email_filter.value = ''
                    status_filter.value = 'Activos'
                    created_after.value = ''
                    created_before.value = ''
                    date_range.value = 'Todo el tiempo'
                    state['filters'] = {}
                    state['current_page'] = 1
                    perform_search()
                
                async def show_stats():
                    """Show user statistics."""
                    stats_container.clear()
                    
                    try:
                        async with AsyncSessionLocal() as session:
                            search_service = UserSearchService(session)
                            stats = await search_service.get_search_stats()
                            
                            with stats_container:
                                # Total stats
                                with ui.grid(columns=2).classes('w-full gap-4'):
                                    with ui.card().classes('p-3'):
                                        ui.label('Total de Usuarios').classes('text-sm text-gray-600')
                                        ui.label(str(stats['total_users'])).classes('text-2xl font-bold')
                                    
                                    with ui.card().classes('p-3'):
                                        ui.label('Usuarios Activos').classes('text-sm text-gray-600')
                                        ui.label(str(stats['active_users'])).classes('text-2xl font-bold text-green-600')
                                    
                                    with ui.card().classes('p-3'):
                                        ui.label('Usuarios Eliminados').classes('text-sm text-gray-600')
                                        ui.label(str(stats['deleted_users'])).classes('text-2xl font-bold text-red-600')
                                    
                                    with ui.card().classes('p-3'):
                                        ui.label('Tasa de Eliminación').classes('text-sm text-gray-600')
                                        ui.label(f"{stats['deletion_rate']:.1f}%").classes('text-2xl font-bold')
                                
                                # Recent activity
                                ui.separator()
                                ui.label('Actividad Reciente').classes('font-semibold mt-2')
                                with ui.grid(columns=2).classes('w-full gap-4'):
                                    with ui.card().classes('p-3'):
                                        ui.label('Creados última semana').classes('text-sm text-gray-600')
                                        ui.label(str(stats['recent_activity']['created_last_week'])).classes('text-xl font-bold')
                                    
                                    with ui.card().classes('p-3'):
                                        ui.label('Modificados última semana').classes('text-sm text-gray-600')
                                        ui.label(str(stats['recent_activity']['updated_last_week'])).classes('text-xl font-bold')
                            
                            stats_dialog.open()
                    
                    except Exception as e:
                        ui.notify(f'Error al obtener estadísticas: {str(e)}', type='negative')
                
                async def export_results(format):
                    """Export search results."""
                    try:
                        if not state['search_results']:
                            ui.notify('No hay resultados para exportar', type='warning')
                            return
                        
                        async with AsyncSessionLocal() as session:
                            search_service = UserSearchService(session)
                            
                            # Prepare export parameters
                            export_params = {
                                'search_term': search_input.value,
                                **state['filters']
                            }
                            
                            # Export data
                            exported_data = await search_service.export_search_results(
                                export_params,
                                format=format
                            )
                            
                            # Create download
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"usuarios_export_{timestamp}.{format}"
                            
                            # In a real app, you would trigger a download here
                            # For now, we'll just show a success message
                            ui.notify(f'Datos exportados exitosamente ({len(exported_data)} bytes)', type='positive')
                            
                            # You could also show the data in a dialog or copy to clipboard
                            if len(exported_data) < 10000:  # Only for small exports
                                ui.run_javascript(f'''
                                    navigator.clipboard.writeText(`{exported_data}`);
                                ''')
                                ui.notify('Datos copiados al portapapeles', type='info')
                    
                    except Exception as e:
                        ui.notify(f'Error al exportar: {str(e)}', type='negative')
                
                # Initial load
                await perform_search()