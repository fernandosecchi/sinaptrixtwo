"""Configuration management page for iSeries infrastructure."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from nicegui import ui
from src.database import AsyncSessionLocal
from src.ui.layouts import theme_layout


def create_configuraciones_page():
    """Register the configurations page for iSeries infrastructure management."""

    @ui.page("/configuraciones")
    async def configuraciones_page():
        breadcrumb_items = [
            ('Infraestructura', '/'),
            ('Configuraciones', '/configuraciones')
        ]

        with theme_layout('Configuraciones iSeries', breadcrumb_items=breadcrumb_items):
            with ui.column().classes('w-full max-w-7xl gap-6'):
                # Page header with description
                with ui.card().classes('w-full bg-gradient-to-r from-cyan-50 to-blue-50 border-cyan-200'):
                    with ui.row().classes('items-center gap-4'):
                        ui.icon('settings', size='lg').classes('text-cyan-600')
                        with ui.column().classes('gap-1'):
                            ui.label('Configuraciones de Infraestructura iSeries').classes('text-2xl font-bold text-gray-800')
                            ui.label('Gestión centralizada de parámetros y configuraciones para servidores IBM iSeries').classes('text-gray-600')

                # Statistics cards
                with ui.row().classes('w-full gap-4'):
                    # Server configs
                    with ui.card().classes('flex-1 hover:shadow-lg transition-shadow cursor-pointer'):
                        with ui.row().classes('items-center gap-3'):
                            with ui.avatar().props('size=lg color=cyan icon=dns').classes('text-white'):
                                pass
                            with ui.column().classes('gap-0'):
                                ui.label('12').classes('text-2xl font-bold text-gray-800')
                                ui.label('Servidores Configurados').classes('text-sm text-gray-600')

                    # LPAR configs
                    with ui.card().classes('flex-1 hover:shadow-lg transition-shadow cursor-pointer'):
                        with ui.row().classes('items-center gap-3'):
                            with ui.avatar().props('size=lg color=violet icon=developer_board').classes('text-white'):
                                pass
                            with ui.column().classes('gap-0'):
                                ui.label('48').classes('text-2xl font-bold text-gray-800')
                                ui.label('LPARs Activas').classes('text-sm text-gray-600')

                    # Replication configs
                    with ui.card().classes('flex-1 hover:shadow-lg transition-shadow cursor-pointer'):
                        with ui.row().classes('items-center gap-3'):
                            with ui.avatar().props('size=lg color=emerald icon=sync').classes('text-white'):
                                pass
                            with ui.column().classes('gap-0'):
                                ui.label('6').classes('text-2xl font-bold text-gray-800')
                                ui.label('Réplicas Configuradas').classes('text-sm text-gray-600')

                    # Active alerts
                    with ui.card().classes('flex-1 hover:shadow-lg transition-shadow cursor-pointer'):
                        with ui.row().classes('items-center gap-3'):
                            with ui.avatar().props('size=lg color=amber icon=warning').classes('text-white'):
                                pass
                            with ui.column().classes('gap-0'):
                                ui.label('3').classes('text-2xl font-bold text-gray-800')
                                ui.label('Alertas Activas').classes('text-sm text-gray-600')

                # Configuration sections with tabs
                with ui.card().classes('w-full'):
                    with ui.tabs().classes('w-full') as tabs:
                        general_tab = ui.tab('General', icon='tune')
                        network_tab = ui.tab('Red', icon='lan')
                        security_tab = ui.tab('Seguridad', icon='security')
                        backup_tab = ui.tab('Respaldo', icon='backup')
                        monitoring_tab = ui.tab('Monitoreo', icon='monitor_heart')

                    with ui.tab_panels(tabs, value=general_tab).classes('w-full'):
                        # General Configuration Tab
                        with ui.tab_panel(general_tab):
                            with ui.column().classes('gap-6 p-4'):
                                ui.label('Configuración General del Sistema').classes('text-lg font-semibold text-gray-700')

                                # System parameters
                                with ui.row().classes('w-full gap-4'):
                                    with ui.column().classes('flex-1 gap-4'):
                                        ui.input('Nombre del Sistema', value='PROD-iSeries-01').props('outlined dense').classes('w-full')
                                        ui.input('Ubicación', value='Data Center Principal').props('outlined dense').classes('w-full')
                                        ui.select(
                                            'Ambiente',
                                            options=['Producción', 'Desarrollo', 'Testing', 'QA'],
                                            value='Producción'
                                        ).props('outlined dense').classes('w-full')

                                    with ui.column().classes('flex-1 gap-4'):
                                        ui.input('Versión OS/400', value='V7R4M0').props('outlined dense').classes('w-full')
                                        ui.input('Modelo', value='Power9 S924').props('outlined dense').classes('w-full')
                                        ui.number('CPUs Asignados', value=8, min=1, max=64).props('outlined dense').classes('w-full')

                                # Save button
                                with ui.row().classes('w-full justify-end mt-4'):
                                    ui.button('Guardar Cambios', icon='save').props('color=primary')

                        # Network Configuration Tab
                        with ui.tab_panel(network_tab):
                            with ui.column().classes('gap-6 p-4'):
                                ui.label('Configuración de Red').classes('text-lg font-semibold text-gray-700')

                                with ui.row().classes('w-full gap-4'):
                                    with ui.column().classes('flex-1 gap-4'):
                                        ui.input('IP Principal', value='192.168.100.10').props('outlined dense').classes('w-full')
                                        ui.input('Máscara de Red', value='255.255.255.0').props('outlined dense').classes('w-full')
                                        ui.input('Gateway', value='192.168.100.1').props('outlined dense').classes('w-full')

                                    with ui.column().classes('flex-1 gap-4'):
                                        ui.input('DNS Primario', value='8.8.8.8').props('outlined dense').classes('w-full')
                                        ui.input('DNS Secundario', value='8.8.4.4').props('outlined dense').classes('w-full')
                                        ui.input('Dominio', value='sinaptrix.local').props('outlined dense').classes('w-full')

                                # Network interfaces table
                                ui.label('Interfaces de Red').classes('text-md font-medium text-gray-600 mt-4')
                                with ui.table(
                                    columns=[
                                        {'name': 'interface', 'label': 'Interface', 'field': 'interface'},
                                        {'name': 'ip', 'label': 'IP Address', 'field': 'ip'},
                                        {'name': 'status', 'label': 'Estado', 'field': 'status'},
                                        {'name': 'speed', 'label': 'Velocidad', 'field': 'speed'},
                                    ],
                                    rows=[
                                        {'interface': 'ETH0', 'ip': '192.168.100.10', 'status': 'Activo', 'speed': '10 Gbps'},
                                        {'interface': 'ETH1', 'ip': '192.168.100.11', 'status': 'Activo', 'speed': '10 Gbps'},
                                        {'interface': 'ETH2', 'ip': '10.0.0.10', 'status': 'Standby', 'speed': '1 Gbps'},
                                    ]
                                ).classes('w-full'):
                                    pass

                                with ui.row().classes('w-full justify-end mt-4'):
                                    ui.button('Aplicar Configuración', icon='save').props('color=primary')

                        # Security Configuration Tab
                        with ui.tab_panel(security_tab):
                            with ui.column().classes('gap-6 p-4'):
                                ui.label('Configuración de Seguridad').classes('text-lg font-semibold text-gray-700')

                                # Security settings
                                with ui.column().classes('gap-4'):
                                    with ui.card().classes('w-full p-4'):
                                        ui.label('Políticas de Contraseña').classes('text-md font-medium mb-2')
                                        ui.switch('Exigir contraseñas complejas', value=True)
                                        ui.switch('Caducidad de contraseña (90 días)', value=True)
                                        ui.switch('Bloqueo después de 3 intentos fallidos', value=True)

                                    with ui.card().classes('w-full p-4'):
                                        ui.label('Auditoría').classes('text-md font-medium mb-2')
                                        ui.switch('Auditoría de acceso al sistema', value=True)
                                        ui.switch('Auditoría de cambios de configuración', value=True)
                                        ui.switch('Auditoría de comandos ejecutados', value=False)

                                    with ui.card().classes('w-full p-4'):
                                        ui.label('Conexiones Seguras').classes('text-md font-medium mb-2')
                                        ui.switch('Requerir SSL/TLS para conexiones', value=True)
                                        ui.switch('SSH habilitado', value=True)
                                        ui.switch('Telnet habilitado', value=False).props('color=warning')

                                with ui.row().classes('w-full justify-end mt-4'):
                                    ui.button('Actualizar Seguridad', icon='security').props('color=primary')

                        # Backup Configuration Tab
                        with ui.tab_panel(backup_tab):
                            with ui.column().classes('gap-6 p-4'):
                                ui.label('Configuración de Respaldo').classes('text-lg font-semibold text-gray-700')

                                # Backup schedule
                                with ui.row().classes('w-full gap-4'):
                                    with ui.column().classes('flex-1'):
                                        ui.label('Programación de Respaldos').classes('text-md font-medium mb-2')
                                        ui.select(
                                            'Tipo de Respaldo',
                                            options=['Completo', 'Incremental', 'Diferencial'],
                                            value='Completo'
                                        ).props('outlined dense').classes('w-full')
                                        ui.select(
                                            'Frecuencia',
                                            options=['Diario', 'Semanal', 'Mensual'],
                                            value='Diario'
                                        ).props('outlined dense').classes('w-full')
                                        ui.time('Hora de Ejecución', value='02:00').props('outlined dense').classes('w-full')

                                    with ui.column().classes('flex-1'):
                                        ui.label('Destino de Respaldo').classes('text-md font-medium mb-2')
                                        ui.input('Servidor de Respaldo', value='backup.sinaptrix.local').props('outlined dense').classes('w-full')
                                        ui.input('Ruta de Almacenamiento', value='/backups/iseries/').props('outlined dense').classes('w-full')
                                        ui.number('Retención (días)', value=30, min=1).props('outlined dense').classes('w-full')

                                # Recent backups
                                ui.label('Respaldos Recientes').classes('text-md font-medium mt-4')
                                with ui.table(
                                    columns=[
                                        {'name': 'date', 'label': 'Fecha', 'field': 'date'},
                                        {'name': 'type', 'label': 'Tipo', 'field': 'type'},
                                        {'name': 'size', 'label': 'Tamaño', 'field': 'size'},
                                        {'name': 'status', 'label': 'Estado', 'field': 'status'},
                                    ],
                                    rows=[
                                        {'date': '2024-11-19 02:00', 'type': 'Completo', 'size': '450 GB', 'status': 'Exitoso'},
                                        {'date': '2024-11-18 02:00', 'type': 'Incremental', 'size': '12 GB', 'status': 'Exitoso'},
                                        {'date': '2024-11-17 02:00', 'type': 'Incremental', 'size': '8 GB', 'status': 'Exitoso'},
                                    ]
                                ).classes('w-full'):
                                    pass

                                with ui.row().classes('w-full justify-end mt-4'):
                                    ui.button('Guardar Configuración', icon='save').props('color=primary')

                        # Monitoring Configuration Tab
                        with ui.tab_panel(monitoring_tab):
                            with ui.column().classes('gap-6 p-4'):
                                ui.label('Configuración de Monitoreo').classes('text-lg font-semibold text-gray-700')

                                # Monitoring thresholds
                                with ui.row().classes('w-full gap-4'):
                                    with ui.column().classes('flex-1'):
                                        ui.label('Umbrales de Alerta').classes('text-md font-medium mb-2')
                                        ui.slider('CPU (%)', min=0, max=100, value=80).props('label-always').classes('w-full')
                                        ui.slider('Memoria (%)', min=0, max=100, value=85).props('label-always').classes('w-full')
                                        ui.slider('Disco (%)', min=0, max=100, value=90).props('label-always').classes('w-full')

                                    with ui.column().classes('flex-1'):
                                        ui.label('Notificaciones').classes('text-md font-medium mb-2')
                                        ui.input('Email de Alertas', value='admin@sinaptrix.com').props('outlined dense').classes('w-full')
                                        ui.switch('Alertas por Email', value=True)
                                        ui.switch('Alertas por SMS', value=False)
                                        ui.switch('Integración con Slack', value=True)

                                # Monitoring status
                                ui.label('Estado Actual del Sistema').classes('text-md font-medium mt-4')
                                with ui.row().classes('w-full gap-4'):
                                    # CPU gauge
                                    with ui.card().classes('flex-1 p-4'):
                                        ui.label('CPU').classes('text-center font-medium')
                                        ui.circular_progress(value=0.45, size='lg', color='green').classes('mx-auto')
                                        ui.label('45%').classes('text-center text-sm text-gray-600')

                                    # Memory gauge
                                    with ui.card().classes('flex-1 p-4'):
                                        ui.label('Memoria').classes('text-center font-medium')
                                        ui.circular_progress(value=0.62, size='lg', color='amber').classes('mx-auto')
                                        ui.label('62%').classes('text-center text-sm text-gray-600')

                                    # Disk gauge
                                    with ui.card().classes('flex-1 p-4'):
                                        ui.label('Disco').classes('text-center font-medium')
                                        ui.circular_progress(value=0.78, size='lg', color='orange').classes('mx-auto')
                                        ui.label('78%').classes('text-center text-sm text-gray-600')

                                    # Network gauge
                                    with ui.card().classes('flex-1 p-4'):
                                        ui.label('Red').classes('text-center font-medium')
                                        ui.circular_progress(value=0.25, size='lg', color='blue').classes('mx-auto')
                                        ui.label('25 Mbps').classes('text-center text-sm text-gray-600')

                                with ui.row().classes('w-full justify-end mt-4'):
                                    ui.button('Aplicar Configuración', icon='save').props('color=primary')

                # Quick Actions
                with ui.card().classes('w-full'):
                    ui.label('Acciones Rápidas').classes('text-lg font-semibold mb-4')
                    with ui.row().classes('gap-2'):
                        ui.button('Exportar Configuración', icon='download').props('outline color=primary')
                        ui.button('Importar Configuración', icon='upload').props('outline color=secondary')
                        ui.button('Validar Configuración', icon='check_circle').props('outline color=positive')
                        ui.button('Restaurar Valores por Defecto', icon='restore').props('outline color=warning')