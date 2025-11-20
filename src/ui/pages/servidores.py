"""Servers management page for iSeries infrastructure."""
from datetime import datetime
from typing import List, Optional
from nicegui import ui
from src.database import AsyncSessionLocal
from src.ui.layouts import theme_layout
from src.services.infrastructure.servidor_service import ServidorService
from src.models.infrastructure.servidor import (
    Servidor,
    ProcessorTier,
    EstadoRegistro,
    TipoStorage
)


def create_servidores_page():
    """Register the servers management page."""

    @ui.page("/servidores")
    async def servidores_page():
        breadcrumb_items = [
            ('Infraestructura', '/'),
            ('Servidores iSeries', '/servidores')
        ]

        with theme_layout('Servidores iSeries', breadcrumb_items=breadcrumb_items):
            # Page state
            servers_list = []
            selected_server = None

            async def load_servers():
                """Load servers from database."""
                nonlocal servers_list
                try:
                    async with AsyncSessionLocal() as session:
                        service = ServidorService(session)
                        servers_list = await service.list_servidores()

                        # Get statistics
                        stats = await service.get_statistics()

                        # Update statistics cards
                        total_label.text = str(stats['total_servers'])
                        active_label.text = str(stats['active_servers'])
                        virtual_label.text = str(stats['virtualized_servers'])
                        physical_label.text = str(stats['physical_servers'])

                        # Update table
                        servers_table.rows = format_servers_for_table(servers_list)
                        servers_table.update()

                except Exception as e:
                    ui.notify(f'Error cargando servidores: {str(e)}', type='negative')

            def format_servers_for_table(servers: List[Servidor]) -> List[dict]:
                """Format servers for table display."""
                rows = []
                for server in servers:
                    rows.append({
                        'id': server.id,
                        'nombre': server.nombre_servidor or f"Servidor {server.id}",
                        'modelo': server.modelo,
                        'processor': f"{server.processor_feature_code} ({server.processor_tier.value})",
                        'estado': format_estado_badge(server.estado_registro),
                        'ubicacion': server.ubicacion or 'No especificada',
                        'virtualizado': 'Sí' if server.es_virtualizado else 'No',
                        'activo': format_activo_badge(server.activo),
                        'serie': server.numero_serie or '-',
                        'actions': server.id
                    })
                return rows

            def format_estado_badge(estado: EstadoRegistro) -> str:
                """Format status as HTML badge."""
                colors = {
                    EstadoRegistro.PRELIMINAR: 'amber',
                    EstadoRegistro.CONFIRMADO: 'green',
                    EstadoRegistro.REVISION: 'blue',
                    EstadoRegistro.OBSOLETO: 'red'
                }
                color = colors.get(estado, 'gray')
                return f'<span class="px-2 py-1 rounded text-xs font-medium bg-{color}-100 text-{color}-800">{estado.value}</span>'

            def format_activo_badge(activo: bool) -> str:
                """Format active status as HTML badge."""
                if activo:
                    return '<span class="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">Activo</span>'
                else:
                    return '<span class="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">Inactivo</span>'

            async def create_server():
                """Open dialog to create new server."""
                with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
                    ui.label('Nuevo Servidor iSeries').classes('text-2xl font-bold mb-4')

                    with ui.tabs().classes('w-full') as tabs:
                        quotation_tab = ui.tab('Cotización', icon='request_quote')
                        technical_tab = ui.tab('Técnico', icon='settings')
                        network_tab = ui.tab('Red', icon='lan')
                        notes_tab = ui.tab('Notas', icon='notes')

                    with ui.tab_panels(tabs, value=quotation_tab).classes('w-full'):
                        # Quotation Tab - Required fields for pricing
                        with ui.tab_panel(quotation_tab):
                            with ui.column().classes('gap-4'):
                                ui.label('Información para Cotización').classes('font-medium text-gray-700')

                                with ui.row().classes('w-full gap-4'):
                                    modelo_input = ui.input(
                                        'Modelo *',
                                        placeholder='Ej: 9009-42A, 8203-E4A'
                                    ).props('outlined dense').classes('flex-1')

                                    processor_code_input = ui.input(
                                        'Processor Feature Code *',
                                        placeholder='Ej: EP30, EPX5'
                                    ).props('outlined dense').classes('flex-1')

                                with ui.row().classes('w-full gap-4'):
                                    processor_tier_select = ui.select(
                                        options=[tier.value for tier in ProcessorTier],
                                        label='Processor Tier *',
                                        value=ProcessorTier.P10.value
                                    ).props('outlined dense').classes('flex-1')

                                    ubicacion_input = ui.input(
                                        'Ubicación',
                                        placeholder='Datacenter, On-premise, Cloud'
                                    ).props('outlined dense').classes('flex-1')

                                with ui.row().classes('w-full gap-4'):
                                    virtualizado_switch = ui.switch('Virtualizado con PowerVM')

                                    estado_select = ui.select(
                                        options=[estado.value for estado in EstadoRegistro],
                                        label='Estado del Registro',
                                        value=EstadoRegistro.PRELIMINAR.value
                                    ).props('outlined dense').classes('flex-1')

                        # Technical Tab - Optional technical details
                        with ui.tab_panel(technical_tab):
                            with ui.column().classes('gap-4'):
                                ui.label('Información Técnica').classes('font-medium text-gray-700')

                                with ui.row().classes('w-full gap-4'):
                                    nombre_input = ui.input(
                                        'Nombre del Servidor',
                                        placeholder='Identificador único'
                                    ).props('outlined dense').classes('flex-1')

                                    descripcion_input = ui.input(
                                        'Descripción',
                                        placeholder='Alias o descripción'
                                    ).props('outlined dense').classes('flex-1')

                                with ui.row().classes('w-full gap-4'):
                                    serie_input = ui.input(
                                        'Número de Serie',
                                        placeholder='Serial del chasis'
                                    ).props('outlined dense').classes('flex-1')

                                    machine_type_input = ui.input(
                                        'Machine Type',
                                        placeholder='Ej: 9009'
                                    ).props('outlined dense').classes('flex-1')

                                    frame_input = ui.input(
                                        'Frame ID',
                                        placeholder='ID del frame'
                                    ).props('outlined dense').classes('flex-1')

                                with ui.row().classes('w-full gap-4'):
                                    firmware_input = ui.input(
                                        'Firmware Version',
                                        placeholder='Versión del firmware'
                                    ).props('outlined dense').classes('flex-1')

                                    os_version_input = ui.input(
                                        'OS Version',
                                        placeholder='Ej: V7R4M0'
                                    ).props('outlined dense').classes('flex-1')

                                with ui.row().classes('w-full gap-4'):
                                    procesadores_input = ui.number(
                                        'Procesadores Físicos',
                                        min=1,
                                        max=256
                                    ).props('outlined dense').classes('flex-1')

                                    memoria_input = ui.number(
                                        'Memoria Total (MB)',
                                        min=1024
                                    ).props('outlined dense').classes('flex-1')

                                    storage_select = ui.select(
                                        options=[tipo.value for tipo in TipoStorage],
                                        label='Tipo de Storage',
                                        with_input=True
                                    ).props('outlined dense clearable').classes('flex-1')

                        # Network Tab
                        with ui.tab_panel(network_tab):
                            with ui.column().classes('gap-4'):
                                ui.label('Configuración de Red').classes('font-medium text-gray-700')

                                ip_input = ui.input(
                                    'IP Principal',
                                    placeholder='Dirección IP principal'
                                ).props('outlined dense').classes('w-full')

                        # Notes Tab
                        with ui.tab_panel(notes_tab):
                            with ui.column().classes('gap-4'):
                                ui.label('Notas y Observaciones').classes('font-medium text-gray-700')

                                notas_input = ui.textarea(
                                    'Notas',
                                    placeholder='Observaciones adicionales sobre el servidor'
                                ).props('outlined').classes('w-full')

                    # Dialog actions
                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancelar', on_click=dialog.close).props('flat')

                        async def save_server():
                            """Save new server."""
                            try:
                                # Validate required fields
                                if not modelo_input.value:
                                    ui.notify('El modelo es obligatorio', type='warning')
                                    return

                                if not processor_code_input.value:
                                    ui.notify('El Processor Feature Code es obligatorio', type='warning')
                                    return

                                async with AsyncSessionLocal() as session:
                                    service = ServidorService(session)

                                    # Create server
                                    await service.create_servidor(
                                        modelo=modelo_input.value,
                                        processor_feature_code=processor_code_input.value,
                                        processor_tier=ProcessorTier(processor_tier_select.value),
                                        nombre_servidor=nombre_input.value or None,
                                        descripcion=descripcion_input.value or None,
                                        ubicacion=ubicacion_input.value or None,
                                        es_virtualizado=virtualizado_switch.value,
                                        estado_registro=EstadoRegistro(estado_select.value),
                                        numero_serie=serie_input.value or None,
                                        machine_type=machine_type_input.value or None,
                                        frame_id=frame_input.value or None,
                                        firmware_version=firmware_input.value or None,
                                        cantidad_procesadores_fisicos=procesadores_input.value if procesadores_input.value else None,
                                        memoria_total_mb=memoria_input.value if memoria_input.value else None,
                                        tipo_storage=TipoStorage(storage_select.value) if storage_select.value else None,
                                        os_version=os_version_input.value or None,
                                        ip_principal=ip_input.value or None,
                                        notas=notas_input.value or None
                                    )

                                    await session.commit()

                                ui.notify('Servidor creado exitosamente', type='positive')
                                await load_servers()
                                dialog.close()

                            except Exception as e:
                                ui.notify(f'Error al crear servidor: {str(e)}', type='negative')

                        ui.button('Guardar', on_click=save_server).props('color=primary')

                dialog.open()

            async def edit_server(server_id: int):
                """Edit existing server."""
                try:
                    async with AsyncSessionLocal() as session:
                        service = ServidorService(session)
                        server = await service.get_servidor(server_id)

                        if not server:
                            ui.notify('Servidor no encontrado', type='negative')
                            return

                    with ui.dialog() as dialog, ui.card().classes('w-full max-w-4xl'):
                        ui.label(f'Editar Servidor: {server.display_name}').classes('text-2xl font-bold mb-4')

                        with ui.tabs().classes('w-full') as tabs:
                            quotation_tab = ui.tab('Cotización', icon='request_quote')
                            technical_tab = ui.tab('Técnico', icon='settings')
                            network_tab = ui.tab('Red', icon='lan')
                            notes_tab = ui.tab('Notas', icon='notes')

                        with ui.tab_panels(tabs, value=quotation_tab).classes('w-full'):
                            # Quotation Tab
                            with ui.tab_panel(quotation_tab):
                                with ui.column().classes('gap-4'):
                                    ui.label('Información para Cotización').classes('font-medium text-gray-700')

                                    with ui.row().classes('w-full gap-4'):
                                        modelo_edit = ui.input(
                                            'Modelo *',
                                            value=server.modelo
                                        ).props('outlined dense').classes('flex-1')

                                        processor_code_edit = ui.input(
                                            'Processor Feature Code *',
                                            value=server.processor_feature_code
                                        ).props('outlined dense').classes('flex-1')

                                    with ui.row().classes('w-full gap-4'):
                                        processor_tier_edit = ui.select(
                                            options=[tier.value for tier in ProcessorTier],
                                            label='Processor Tier *',
                                            value=server.processor_tier.value
                                        ).props('outlined dense').classes('flex-1')

                                        ubicacion_edit = ui.input(
                                            'Ubicación',
                                            value=server.ubicacion or ''
                                        ).props('outlined dense').classes('flex-1')

                                    with ui.row().classes('w-full gap-4'):
                                        virtualizado_edit = ui.switch(
                                            'Virtualizado con PowerVM',
                                            value=server.es_virtualizado
                                        )

                                        estado_edit = ui.select(
                                            options=[estado.value for estado in EstadoRegistro],
                                            label='Estado del Registro',
                                            value=server.estado_registro.value
                                        ).props('outlined dense').classes('flex-1')

                                        activo_edit = ui.switch(
                                            'Servidor Activo',
                                            value=server.activo
                                        )

                            # Technical Tab
                            with ui.tab_panel(technical_tab):
                                with ui.column().classes('gap-4'):
                                    ui.label('Información Técnica').classes('font-medium text-gray-700')

                                    with ui.row().classes('w-full gap-4'):
                                        nombre_edit = ui.input(
                                            'Nombre del Servidor',
                                            value=server.nombre_servidor or ''
                                        ).props('outlined dense').classes('flex-1')

                                        descripcion_edit = ui.input(
                                            'Descripción',
                                            value=server.descripcion or ''
                                        ).props('outlined dense').classes('flex-1')

                                    with ui.row().classes('w-full gap-4'):
                                        serie_edit = ui.input(
                                            'Número de Serie',
                                            value=server.numero_serie or ''
                                        ).props('outlined dense').classes('flex-1')

                                        machine_type_edit = ui.input(
                                            'Machine Type',
                                            value=server.machine_type or ''
                                        ).props('outlined dense').classes('flex-1')

                                        frame_edit = ui.input(
                                            'Frame ID',
                                            value=server.frame_id or ''
                                        ).props('outlined dense').classes('flex-1')

                                    with ui.row().classes('w-full gap-4'):
                                        firmware_edit = ui.input(
                                            'Firmware Version',
                                            value=server.firmware_version or ''
                                        ).props('outlined dense').classes('flex-1')

                                        os_version_edit = ui.input(
                                            'OS Version',
                                            value=server.os_version or ''
                                        ).props('outlined dense').classes('flex-1')

                                    with ui.row().classes('w-full gap-4'):
                                        procesadores_edit = ui.number(
                                            'Procesadores Físicos',
                                            value=server.cantidad_procesadores_fisicos,
                                            min=1,
                                            max=256
                                        ).props('outlined dense').classes('flex-1')

                                        memoria_edit = ui.number(
                                            'Memoria Total (MB)',
                                            value=server.memoria_total_mb,
                                            min=1024
                                        ).props('outlined dense').classes('flex-1')

                                        storage_edit = ui.select(
                                            options=[tipo.value for tipo in TipoStorage],
                                            label='Tipo de Storage',
                                            value=server.tipo_storage.value if server.tipo_storage else None,
                                            with_input=True
                                        ).props('outlined dense clearable').classes('flex-1')

                            # Network Tab
                            with ui.tab_panel(network_tab):
                                with ui.column().classes('gap-4'):
                                    ui.label('Configuración de Red').classes('font-medium text-gray-700')

                                    ip_edit = ui.input(
                                        'IP Principal',
                                        value=server.ip_principal or ''
                                    ).props('outlined dense').classes('w-full')

                            # Notes Tab
                            with ui.tab_panel(notes_tab):
                                with ui.column().classes('gap-4'):
                                    ui.label('Notas y Observaciones').classes('font-medium text-gray-700')

                                    notas_edit = ui.textarea(
                                        'Notas',
                                        value=server.notas or ''
                                    ).props('outlined').classes('w-full')

                        # Dialog actions
                        with ui.row().classes('w-full justify-end gap-2 mt-4'):
                            ui.button('Cancelar', on_click=dialog.close).props('flat')

                            async def update_server():
                                """Update server."""
                                try:
                                    # Validate required fields
                                    if not modelo_edit.value:
                                        ui.notify('El modelo es obligatorio', type='warning')
                                        return

                                    if not processor_code_edit.value:
                                        ui.notify('El Processor Feature Code es obligatorio', type='warning')
                                        return

                                    async with AsyncSessionLocal() as session:
                                        service = ServidorService(session)

                                        # Update server
                                        await service.update_servidor(
                                            servidor_id=server_id,
                                            modelo=modelo_edit.value,
                                            processor_feature_code=processor_code_edit.value,
                                            processor_tier=ProcessorTier(processor_tier_edit.value),
                                            nombre_servidor=nombre_edit.value or None,
                                            descripcion=descripcion_edit.value or None,
                                            ubicacion=ubicacion_edit.value or None,
                                            es_virtualizado=virtualizado_edit.value,
                                            estado_registro=EstadoRegistro(estado_edit.value),
                                            numero_serie=serie_edit.value or None,
                                            machine_type=machine_type_edit.value or None,
                                            frame_id=frame_edit.value or None,
                                            firmware_version=firmware_edit.value or None,
                                            cantidad_procesadores_fisicos=procesadores_edit.value if procesadores_edit.value else None,
                                            memoria_total_mb=memoria_edit.value if memoria_edit.value else None,
                                            tipo_storage=TipoStorage(storage_edit.value) if storage_edit.value else None,
                                            os_version=os_version_edit.value or None,
                                            ip_principal=ip_edit.value or None,
                                            activo=activo_edit.value,
                                            notas=notas_edit.value or None
                                        )

                                        await session.commit()

                                    ui.notify('Servidor actualizado exitosamente', type='positive')
                                    await load_servers()
                                    dialog.close()

                                except Exception as e:
                                    ui.notify(f'Error al actualizar servidor: {str(e)}', type='negative')

                            ui.button('Actualizar', on_click=update_server).props('color=primary')

                    dialog.open()

                except Exception as e:
                    ui.notify(f'Error al cargar servidor: {str(e)}', type='negative')

            async def delete_server(server_id: int):
                """Delete (deactivate) a server."""
                with ui.dialog() as confirm_dialog, ui.card():
                    ui.label('¿Está seguro que desea eliminar este servidor?').classes('text-lg')
                    ui.label('El servidor será marcado como inactivo y obsoleto.').classes('text-sm text-gray-600')

                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancelar', on_click=confirm_dialog.close).props('flat')

                        async def confirm_delete():
                            try:
                                async with AsyncSessionLocal() as session:
                                    service = ServidorService(session)
                                    await service.delete_servidor(server_id)
                                    await session.commit()

                                ui.notify('Servidor eliminado exitosamente', type='positive')
                                await load_servers()
                                confirm_dialog.close()

                            except Exception as e:
                                ui.notify(f'Error al eliminar servidor: {str(e)}', type='negative')

                        ui.button('Eliminar', on_click=confirm_delete).props('color=negative')

                confirm_dialog.open()

            async def validate_server(server_id: int):
                """Validate server for quotation."""
                try:
                    async with AsyncSessionLocal() as session:
                        service = ServidorService(session)
                        validation = await service.validate_quotation_fields(server_id)

                        with ui.dialog() as dialog, ui.card().classes('w-96'):
                            ui.label('Validación de Cotización').classes('text-xl font-bold mb-4')

                            if validation['valid']:
                                ui.icon('check_circle', size='lg').classes('text-green-600')
                                ui.label('Servidor listo para cotización').classes('text-green-600 font-medium')
                            else:
                                ui.icon('error', size='lg').classes('text-red-600')
                                ui.label('Faltan datos obligatorios').classes('text-red-600 font-medium')

                                if validation['errors']:
                                    ui.label('Errores:').classes('font-medium mt-4')
                                    for error in validation['errors']:
                                        ui.label(f'• {error}').classes('text-sm text-red-600')

                            if validation['warnings']:
                                ui.label('Advertencias:').classes('font-medium mt-4')
                                for warning in validation['warnings']:
                                    ui.label(f'• {warning}').classes('text-sm text-amber-600')

                            ui.button('Cerrar', on_click=dialog.close).props('flat').classes('w-full mt-4')

                        dialog.open()

                except Exception as e:
                    ui.notify(f'Error al validar servidor: {str(e)}', type='negative')

            # Main UI
            with ui.column().classes('w-full max-w-7xl gap-6'):
                # Page header
                with ui.card().classes('w-full bg-gradient-to-r from-cyan-50 to-blue-50 border-cyan-200'):
                    with ui.row().classes('items-center justify-between'):
                        with ui.row().classes('items-center gap-4'):
                            ui.icon('dns', size='lg').classes('text-cyan-600')
                            with ui.column().classes('gap-1'):
                                ui.label('Servidores iSeries').classes('text-2xl font-bold text-gray-800')
                                ui.label('Gestión de servidores IBM Power Systems para cotización y seguimiento').classes('text-gray-600')

                        ui.button('Nuevo Servidor', icon='add', on_click=create_server).props('color=primary')

                # Statistics cards
                with ui.row().classes('w-full gap-4'):
                    with ui.card().classes('flex-1'):
                        with ui.row().classes('items-center gap-3'):
                            with ui.avatar().props('size=lg color=cyan icon=dns'):
                                pass
                            with ui.column().classes('gap-0'):
                                total_label = ui.label('0').classes('text-2xl font-bold text-gray-800')
                                ui.label('Total Servidores').classes('text-sm text-gray-600')

                    with ui.card().classes('flex-1'):
                        with ui.row().classes('items-center gap-3'):
                            with ui.avatar().props('size=lg color=green icon=power'):
                                pass
                            with ui.column().classes('gap-0'):
                                active_label = ui.label('0').classes('text-2xl font-bold text-gray-800')
                                ui.label('Servidores Activos').classes('text-sm text-gray-600')

                    with ui.card().classes('flex-1'):
                        with ui.row().classes('items-center gap-3'):
                            with ui.avatar().props('size=lg color=violet icon=cloud'):
                                pass
                            with ui.column().classes('gap-0'):
                                virtual_label = ui.label('0').classes('text-2xl font-bold text-gray-800')
                                ui.label('Virtualizados').classes('text-sm text-gray-600')

                    with ui.card().classes('flex-1'):
                        with ui.row().classes('items-center gap-3'):
                            with ui.avatar().props('size=lg color=amber icon=computer'):
                                pass
                            with ui.column().classes('gap-0'):
                                physical_label = ui.label('0').classes('text-2xl font-bold text-gray-800')
                                ui.label('Físicos').classes('text-sm text-gray-600')

                # Search and filters
                with ui.card().classes('w-full'):
                    with ui.row().classes('w-full gap-4'):
                        search_input = ui.input(
                            'Buscar',
                            placeholder='Buscar por nombre, modelo, serie, IP...'
                        ).props('outlined dense clearable').classes('flex-1')
                        search_input.on('keydown.enter', lambda: load_servers())

                        tier_filter = ui.select(
                            options=['Todos'] + [tier.value for tier in ProcessorTier],
                            label='Processor Tier',
                            value='Todos'
                        ).props('outlined dense').classes('w-48')

                        estado_filter = ui.select(
                            options=['Todos'] + [estado.value for estado in EstadoRegistro],
                            label='Estado',
                            value='Todos'
                        ).props('outlined dense').classes('w-48')

                        ui.button('Buscar', icon='search', on_click=load_servers).props('color=primary')

                # Servers table
                with ui.card().classes('w-full'):
                    servers_table = ui.table(
                        columns=[
                            {'name': 'nombre', 'label': 'Nombre', 'field': 'nombre', 'sortable': True, 'align': 'left'},
                            {'name': 'modelo', 'label': 'Modelo', 'field': 'modelo', 'sortable': True},
                            {'name': 'processor', 'label': 'Procesador', 'field': 'processor'},
                            {'name': 'estado', 'label': 'Estado', 'field': 'estado'},
                            {'name': 'ubicacion', 'label': 'Ubicación', 'field': 'ubicacion'},
                            {'name': 'virtualizado', 'label': 'Virtual', 'field': 'virtualizado'},
                            {'name': 'activo', 'label': 'Activo', 'field': 'activo'},
                            {'name': 'serie', 'label': 'Serie', 'field': 'serie'},
                            {'name': 'actions', 'label': 'Acciones', 'field': 'actions'}
                        ],
                        rows=[],
                        row_key='id'
                    ).classes('w-full')

                    # Custom action buttons in table
                    servers_table.add_slot('body-cell-estado', '''
                        <q-td :props="props">
                            <div v-html="props.value"></div>
                        </q-td>
                    ''')

                    servers_table.add_slot('body-cell-activo', '''
                        <q-td :props="props">
                            <div v-html="props.value"></div>
                        </q-td>
                    ''')

                    servers_table.add_slot('body-cell-actions', '''
                        <q-td :props="props">
                            <q-btn flat round dense icon="visibility" size="sm"
                                @click="$parent.$emit('validate', props.value)"
                                color="info">
                                <q-tooltip>Validar para Cotización</q-tooltip>
                            </q-btn>
                            <q-btn flat round dense icon="edit" size="sm"
                                @click="$parent.$emit('edit', props.value)"
                                color="primary">
                                <q-tooltip>Editar</q-tooltip>
                            </q-btn>
                            <q-btn flat round dense icon="delete" size="sm"
                                @click="$parent.$emit('delete', props.value)"
                                color="negative">
                                <q-tooltip>Eliminar</q-tooltip>
                            </q-btn>
                        </q-td>
                    ''')

                    # Connect events
                    servers_table.on('validate', lambda e: validate_server(e.args))
                    servers_table.on('edit', lambda e: edit_server(e.args))
                    servers_table.on('delete', lambda e: delete_server(e.args))

                # Quick actions
                with ui.card().classes('w-full'):
                    ui.label('Acciones Rápidas').classes('text-lg font-semibold mb-4')
                    with ui.row().classes('gap-2'):
                        ui.button('Exportar Lista', icon='download').props('outline color=primary')
                        ui.button('Importar CSV', icon='upload').props('outline color=secondary')
                        ui.button('Generar Reporte', icon='description').props('outline color=info')
                        ui.button('Validar Todos', icon='fact_check').props('outline color=positive')

            # Load initial data
            await load_servers()