"""Home page of the application."""
from nicegui import ui
from src.ui.layouts import theme_layout


def create_home_page():
    """Register the home page route."""
    
    @ui.page("/")
    def main_page():
        with theme_layout('Inicio'):
            with ui.card().classes('w-full max-w-3xl p-6'):
                ui.label('¡Bienvenido!').classes('text-3xl font-bold text-primary mb-2')
                ui.markdown('Esta es la estructura base de tu aplicación **SinaptrixTwo**.')
                
                ui.separator().classes('my-6')
                
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1'):
                        ui.label('Componentes Dinámicos').classes('text-xl font-semibold mb-2')
                        ui.label('NiceGUI permite interactuar con Python directamente desde el frontend sin escribir JavaScript.')
                        
                        # Interactive example
                        with ui.row().classes('items-center mt-4 gap-2'):
                            name = ui.input('Tu nombre').props('outlined dense').classes('w-64')
                            ui.button('Saludar', on_click=lambda: ui.notify(f'Hola, {name.value}!', type='positive'))

                    with ui.column().classes('flex-1 bg-slate-100 p-4 rounded'):
                        ui.label('Estado del Sistema').classes('font-bold')
                        ui.label('Base de Datos: Conectada (Asyncpg)').classes('text-sm text-green-600')
                        ui.label('Docker: Activo').classes('text-sm text-blue-600')