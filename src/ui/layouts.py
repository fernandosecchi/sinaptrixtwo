"""Shared layouts for the application UI."""
from contextlib import contextmanager
from nicegui import ui


@contextmanager
def theme_layout(page_title: str):
    """Common layout for all pages with Header, Drawer and Footer."""
    # Page Title
    ui.page_title(page_title)

    # Header
    with ui.header().classes('bg-slate-800 text-white shadow-md items-center') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        ui.label('SinaptrixTwo').classes('text-lg font-bold ml-2')
        ui.space()
        # Dark mode toggle
        dark = ui.dark_mode()
        ui.button(icon='dark_mode', on_click=lambda: dark.enable()) \
            .props('flat color=white').bind_visibility_from(dark, 'value', value=False)
        ui.button(icon='light_mode', on_click=lambda: dark.disable()) \
            .props('flat color=white').bind_visibility_from(dark, 'value', value=True)

    # Drawer (Sidebar)
    with ui.left_drawer(value=False).classes('bg-slate-50') as left_drawer:
        ui.label('Navegación').classes('text-xl font-bold p-4 text-slate-700')
        ui.separator()
        with ui.column().classes('w-full gap-0'):
            ui.link('Inicio', '/').classes('w-full p-4 hover:bg-slate-200 text-slate-800 no-underline')
            ui.link('Leads', '/leads').classes('w-full p-4 hover:bg-slate-200 text-slate-800 no-underline')
            ui.link('Usuarios', '/usuarios').classes('w-full p-4 hover:bg-slate-200 text-slate-800 no-underline')

    # Main Content Area
    with ui.column().classes('w-full p-4 md:p-8 items-center'):
        # Yield control to the actual page content
        yield

    # Footer
    with ui.footer().classes('bg-slate-900 text-slate-400 p-2 text-center text-xs'):
        ui.label('Powered by FastAPI + NiceGUI')