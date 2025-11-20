"""Empresas management page with comprehensive CRUD operations."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from nicegui import ui
from src.database import AsyncSessionLocal
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
from src.services.empresas.empresa_service import EmpresaService
from src.services.locations.location_service import LocationService


def create_empresas_page():
    """Register the empresas management page with reusable components."""

    @ui.page("/empresas")
    async def empresas_page():
        breadcrumb_items = [
            ('Gestión', '/'),
            ('Empresas', '/empresas')
        ]
        with theme_layout('Empresas', breadcrumb_items=breadcrumb_items):
            with ui.column().classes('w-full gap-2'):
                # Compact header with add button and filters
                with ui.row().classes('w-full items-center justify-between mb-2'):
                    with ui.row().classes('gap-2'):
                        ui.button('Nueva Empresa', on_click=lambda: empresa_dialog.open(DialogMode.CREATE), icon='business').props('size=sm color=primary')

                        # Quick filters
                        with ui.row().classes('gap-2 items-center'):
                            filter_es_cliente = ui.switch('Clientes').props('size=sm')
                            filter_es_proveedor = ui.switch('Proveedores').props('size=sm')
                            filter_es_partner = ui.switch('Partners').props('size=sm')

                            # Add change handlers
                            filter_es_cliente.on('change', lambda: load_empresas())
                            filter_es_proveedor.on('change', lambda: load_empresas())
                            filter_es_partner.on('change', lambda: load_empresas())

                # Search bar component
                async def search_empresas(search_term: str):
                    await load_empresas(search_term, update_stats=False)

                async def clear_search():
                    await load_empresas(None, update_stats=False)

                search_bar = SearchBar(
                    placeholder="Buscar por nombre, RUT, industria...",
                    on_search=search_empresas,
                    on_clear=clear_search,
                    search_button_text='',  # Icon only
                    clear_button_text=''     # Icon only
                )

                # Stats and refresh in same row
                with ui.row().classes('w-full gap-2 items-center mb-2'):
                    # Estado filter
                    estado_select = ui.select(
                        label='Estado',
                        options=['todos', 'activo', 'inactivo', 'prospecto', 'cliente'],
                        value='todos'
                    ).props('dense outlined').classes('w-32')
                    estado_select.on('change', lambda: load_empresas())

                    ui.space()  # Push stats to the right

                    # Minimal stats container
                    stats_container = ui.row().classes('gap-2 items-center')

                    # Refresh button
                    ui.button(icon='refresh', on_click=lambda: load_empresas()).props('size=sm flat dense color=gray')

                # Location data storage
                location_data = {
                    'countries': [],
                    'states': {},
                    'cities': {}
                }

                async def load_location_data():
                    """Load location data for dropdowns."""
                    async with AsyncSessionLocal() as session:
                        location_service = LocationService(session)

                        # Load all countries
                        countries = await location_service.get_all_countries()
                        location_data['countries'] = [
                            {'label': c.name, 'value': c.id}
                            for c in countries
                        ]

                async def load_states(country_id: int):
                    """Load states for a country."""
                    if country_id and country_id not in location_data['states']:
                        async with AsyncSessionLocal() as session:
                            location_service = LocationService(session)
                            states = await location_service.get_states_by_country(country_id)
                            location_data['states'][country_id] = [
                                {'label': s.name, 'value': s.id}
                                for s in states
                            ]
                    return location_data['states'].get(country_id, [])

                async def load_cities(state_id: int):
                    """Load cities for a state."""
                    if state_id and state_id not in location_data['cities']:
                        async with AsyncSessionLocal() as session:
                            location_service = LocationService(session)
                            cities = await location_service.get_cities_by_state(state_id)
                            location_data['cities'][state_id] = [
                                {'label': c.name, 'value': c.id}
                                for c in cities
                            ]
                    return location_data['cities'].get(state_id, [])

                # Load initial location data
                await load_location_data()

                # Define save_empresa function before using it
                async def save_empresa(data: dict, mode: DialogMode):
                    """Save empresa using the dialog data."""
                    try:
                        async with AsyncSessionLocal() as session:
                            empresa_service = EmpresaService(session)

                            # Prepare data
                            empresa_data = {
                                'nombre': data['nombre'],
                                'nombre_comercial': data.get('nombre_comercial'),
                                'razon_social': data.get('razon_social'),
                                'rut': data.get('rut'),
                                'tipo_empresa': data.get('tipo_empresa'),
                                'industria': data.get('industria'),
                                'telefono_principal': data.get('telefono_principal'),
                                'email_principal': data.get('email_principal'),
                                'sitio_web': data.get('sitio_web'),
                                'direccion': data.get('direccion'),
                                'country_id': data.get('country_id') if data.get('country_id') else None,
                                'state_id': data.get('state_id') if data.get('state_id') else None,
                                'city_id': data.get('city_id') if data.get('city_id') else None,
                                'es_cliente': data.get('es_cliente', False),
                                'es_proveedor': data.get('es_proveedor', False),
                                'es_partner': data.get('es_partner', False),
                                'estado': data.get('estado', 'activo')
                            }

                            if mode == DialogMode.CREATE:
                                empresa = await empresa_service.create_empresa(**empresa_data)
                                message = f'Empresa {data["nombre"]} creada exitosamente'
                            else:  # EDIT mode
                                empresa = await empresa_service.update_empresa(
                                    empresa_id=data['id'],
                                    **empresa_data
                                )
                                message = f'Empresa actualizada exitosamente'

                        ui.notify(message, type='positive')
                        await load_empresas()

                    except ValueError as e:
                        ui.notify(str(e), type='warning')
                    except Exception as e:
                        ui.notify(f'Error: {e}', type='negative')

                async def delete_empresa(data: dict):
                    """Soft delete an empresa."""
                    try:
                        async with AsyncSessionLocal() as session:
                            empresa_service = EmpresaService(session)

                            # Try to delete (will check for servers)
                            result = await empresa_service.delete_empresa(data['id'])

                            if result:
                                ui.notify('Empresa eliminada exitosamente', type='info')
                                await load_empresas()
                            else:
                                ui.notify('No se encontró la empresa', type='warning')

                    except ValueError as e:
                        # This happens if empresa has servers
                        ui.notify(str(e), type='warning')
                    except Exception as e:
                        ui.notify(f'Error: {e}', type='negative')

                # Servidor management dialog
                servidor_dialog = ui.dialog()
                with servidor_dialog, ui.card().classes('w-[700px]'):
                    servidor_dialog_title = ui.label('').classes('text-xl font-semibold mb-4')

                    # Empresa info display
                    empresa_info_label = ui.label('').classes('text-gray-600 mb-4')

                    ui.separator()

                    # Servidores section
                    ui.label('Servidores Asociados').classes('text-lg font-medium mb-2')
                    servidores_container = ui.column().classes('w-full gap-2 max-h-96 overflow-y-auto')

                    # Actions
                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cerrar', on_click=servidor_dialog.close).props('flat')

                async def view_servidores(empresa_data):
                    """View servers associated with an empresa."""
                    servidor_dialog_title.text = 'Servidores de la Empresa'
                    rut_text = f"(RUT: {empresa_data.get('rut')})" if empresa_data.get('rut') else ''
                    empresa_info_label.text = f"Empresa: {empresa_data['nombre']} {rut_text}"

                    # Load empresa with servers
                    async with AsyncSessionLocal() as session:
                        empresa_service = EmpresaService(session)
                        empresa = await empresa_service.get_empresa_by_id(
                            empresa_data['id'],
                            include_relationships=True
                        )

                    # Clear and populate servers
                    servidores_container.clear()
                    with servidores_container:
                        if empresa and empresa.servidores:
                            for servidor in empresa.servidores:
                                with ui.card().classes('w-full'):
                                    with ui.column().classes('gap-1'):
                                        with ui.row().classes('items-center gap-2'):
                                            ui.icon('dns').classes('text-blue-500')
                                            ui.label(servidor.nombre).classes('font-medium')
                                            if servidor.estado == 'activo':
                                                ui.chip('Activo', color='green').props('size=sm')
                                            elif servidor.estado == 'inactivo':
                                                ui.chip('Inactivo', color='orange').props('size=sm')
                                            else:
                                                ui.chip(servidor.estado, color='gray').props('size=sm')

                                        if servidor.ip_principal:
                                            ui.label(f'IP: {servidor.ip_principal}').classes('text-sm text-gray-600')
                                        if servidor.sistema_operativo:
                                            ui.label(f'SO: {servidor.sistema_operativo}').classes('text-sm text-gray-600')
                                        if servidor.tipo_servidor:
                                            ui.label(f'Tipo: {servidor.tipo_servidor}').classes('text-sm text-gray-600')
                        else:
                            ui.label('No hay servidores asociados a esta empresa').classes('text-gray-500 italic')

                    servidor_dialog.open()

                # Create empresa dialog with dynamic location fields
                empresa_dialog = CrudDialog(
                    title="Empresa",
                    fields=[
                        # Basic Information
                        FormField('nombre', 'Nombre', required=True),
                        FormField('nombre_comercial', 'Nombre Comercial', full_width=False),
                        FormField('razon_social', 'Razón Social', full_width=False),
                        FormField('rut', 'RUT/Tax ID', full_width=False),

                        # Business Information
                        FormField('tipo_empresa', 'Tipo de Empresa', field_type='select',
                                options=[
                                    {'label': 'S.A.', 'value': 'sa'},
                                    {'label': 'S.R.L.', 'value': 'srl'},
                                    {'label': 'LTDA', 'value': 'ltda'},
                                    {'label': 'Unipersonal', 'value': 'unipersonal'},
                                    {'label': 'Otra', 'value': 'otra'}
                                ], full_width=False),
                        FormField('industria', 'Industria', full_width=False),

                        # Contact Information
                        FormField('telefono_principal', 'Teléfono Principal', full_width=False),
                        FormField('email_principal', 'Email Principal', field_type='email', full_width=False),
                        FormField('sitio_web', 'Sitio Web', full_width=False),

                        # Location (will be replaced with dynamic dropdowns)
                        FormField('country_id', 'País', field_type='select',
                                options=location_data['countries'], full_width=False),
                        FormField('state_id', 'Estado/Provincia', field_type='select',
                                options=[], full_width=False),
                        FormField('city_id', 'Ciudad', field_type='select',
                                options=[], full_width=False),
                        FormField('direccion', 'Dirección'),

                        # Status
                        FormField('estado', 'Estado', field_type='select',
                                options=[
                                    {'label': 'Activo', 'value': 'activo'},
                                    {'label': 'Inactivo', 'value': 'inactivo'},
                                    {'label': 'Prospecto', 'value': 'prospecto'},
                                    {'label': 'Cliente', 'value': 'cliente'}
                                ], full_width=False),

                        # Relationship flags
                        FormField('es_cliente', 'Es Cliente', field_type='checkbox', full_width=False),
                        FormField('es_proveedor', 'Es Proveedor', field_type='checkbox', full_width=False),
                        FormField('es_partner', 'Es Partner', field_type='checkbox', full_width=False),
                    ],
                    on_save=save_empresa,
                    on_delete=delete_empresa,
                    width='w-[700px]'
                )

                # Data table with columns
                columns = [
                    TableColumn('id', 'ID', 'id'),
                    TableColumn('nombre', 'Nombre', 'nombre'),
                    TableColumn('rut', 'RUT', 'rut'),
                    TableColumn('industria', 'Industria', 'industria'),
                    TableColumn('tipo_relacion', 'Tipo', 'tipo_relacion'),
                    TableColumn('estado', 'Estado', 'estado',
                              format_fn=lambda x: x.capitalize() if x else ''),
                    TableColumn('servidor_count', 'Servidores', 'servidor_count',
                              format_fn=lambda x: str(x) if x else '0'),
                    TableColumn('created_at', 'Creado', 'created_at',
                              format_fn=lambda x: x.strftime("%d/%m/%Y") if x else ''),
                ]

                # Add custom actions to show servers
                def get_custom_actions(row):
                    """Get custom actions for each row."""
                    actions = []
                    if row.get('servidor_count', 0) > 0:
                        actions.append({
                            'icon': 'dns',
                            'tooltip': f"Ver {row['servidor_count']} servidor(es)",
                            'handler': lambda: view_servidores(row)
                        })
                    return actions

                # Create table
                data_table = DataTable(
                    title="",
                    columns=columns,
                    rows_per_page=10,
                    on_view=lambda row: view_empresa(row),
                    on_edit=lambda row: edit_empresa(row),
                    on_delete=lambda row: confirm_delete(row),
                    searchable_fields=['nombre', 'nombre_comercial', 'rut', 'industria'],
                    show_stats=False
                )

                def view_empresa(row):
                    """View empresa details."""
                    empresa_dialog.open(DialogMode.VIEW, row)

                def edit_empresa(row):
                    """Edit empresa."""
                    empresa_dialog.open(DialogMode.EDIT, row)

                def confirm_delete(row):
                    """Confirm empresa deletion."""
                    ConfirmDialog.ask(
                        title='Eliminar Empresa',
                        message=f'¿Estás seguro de eliminar la empresa {row["nombre"]}?',
                        on_confirm=lambda: delete_empresa(row),
                        confirm_color='negative',
                        icon='warning',
                        icon_color='red'
                    )

                async def load_stats():
                    """Load and display empresa statistics."""
                    try:
                        async with AsyncSessionLocal() as session:
                            empresa_service = EmpresaService(session)
                            stats = await empresa_service.get_statistics()

                            # Clear and recreate minimal stats
                            stats_container.clear()

                            with stats_container:
                                # Ultra compact stats - just numbers with tooltips
                                ui.label(f'{stats["total"]}').classes('text-xs text-gray-600').tooltip('Total')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{stats["clientes"]}').classes('text-xs text-blue-600').tooltip('Clientes')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{stats["proveedores"]}').classes('text-xs text-green-600').tooltip('Proveedores')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{stats["partners"]}').classes('text-xs text-purple-600').tooltip('Partners')

                    except Exception as e:
                        ui.notify(f'Error al cargar estadísticas: {e}', type='negative')

                async def load_empresas(search_term: str = None, update_stats: bool = True):
                    """Load and display empresas in the table."""
                    # Only update stats on initial load or explicit request
                    if update_stats:
                        await load_stats()

                    try:
                        async with AsyncSessionLocal() as session:
                            empresa_service = EmpresaService(session)

                            # Build filters
                            estado_filter = None if estado_select.value == 'todos' else estado_select.value
                            es_cliente_filter = filter_es_cliente.value if filter_es_cliente.value else None
                            es_proveedor_filter = filter_es_proveedor.value if filter_es_proveedor.value else None
                            es_partner_filter = filter_es_partner.value if filter_es_partner.value else None

                            # Get empresas
                            empresas = await empresa_service.list_empresas(
                                skip=0,
                                limit=1000,  # Load all for now
                                search=search_term,
                                estado=estado_filter,
                                es_cliente=es_cliente_filter,
                                es_proveedor=es_proveedor_filter,
                                es_partner=es_partner_filter
                            )

                            # Convert to dict for table
                            empresas_data = []
                            for empresa in empresas:
                                # Determine tipo_relacion
                                tipos = []
                                if empresa.es_cliente:
                                    tipos.append('Cliente')
                                if empresa.es_proveedor:
                                    tipos.append('Proveedor')
                                if empresa.es_partner:
                                    tipos.append('Partner')
                                tipo_relacion = ', '.join(tipos) if tipos else 'Ninguno'

                                empresas_data.append({
                                    'id': empresa.id,
                                    'nombre': empresa.nombre,
                                    'nombre_comercial': empresa.nombre_comercial,
                                    'razon_social': empresa.razon_social,
                                    'rut': empresa.rut,
                                    'tipo_empresa': empresa.tipo_empresa,
                                    'industria': empresa.industria,
                                    'telefono_principal': empresa.telefono_principal,
                                    'email_principal': empresa.email_principal,
                                    'sitio_web': empresa.sitio_web,
                                    'country_id': empresa.country_id,
                                    'state_id': empresa.state_id,
                                    'city_id': empresa.city_id,
                                    'direccion': empresa.direccion,
                                    'estado': empresa.estado,
                                    'es_cliente': empresa.es_cliente,
                                    'es_proveedor': empresa.es_proveedor,
                                    'es_partner': empresa.es_partner,
                                    'tipo_relacion': tipo_relacion,
                                    'servidor_count': len(empresa.servidores) if hasattr(empresa, 'servidores') else 0,
                                    'created_at': empresa.created_at,
                                    'updated_at': empresa.updated_at
                                })

                            # Load data into table
                            data_table.load_data(empresas_data)

                    except Exception as e:
                        ui.notify(f'Error al cargar empresas: {e}', type='negative')

                # Load initial data
                await load_empresas()