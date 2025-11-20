"""Shared layouts for the application UI."""
from contextlib import contextmanager
from typing import Optional, List
from nicegui import ui
from src.ui.components.header import AppHeader
from src.ui.components.navigation_drawer import NavigationDrawer, NavItem
from src.ui.components.footer import AppFooter


# Store drawer instance globally to access from pages
_drawer_instance = None


def get_drawer():
    """Get the current drawer instance."""
    return _drawer_instance


@contextmanager
def theme_layout(
    page_title: str,
    show_breadcrumb: bool = True,
    breadcrumb_items: Optional[List[tuple]] = None
):
    """
    Common layout for all pages with Header, Drawer and Footer.

    Args:
        page_title: Title for the page
        show_breadcrumb: Whether to show breadcrumbs
        breadcrumb_items: List of (label, path) tuples for breadcrumb
    """
    global _drawer_instance

    # Import design system
    from src.ui.theme.design_system import apply_custom_styles, NAVIGATION

    # Page Title
    ui.page_title(f'Sinaptrix - {page_title}')

    # Configure page style with custom CSS
    ui.query('body').style('margin: 0; padding: 0; font-family: Inter, -apple-system, sans-serif')

    # Inject custom styles
    ui.html(apply_custom_styles(), sanitize=False)

    # Create navigation drawer component with sections
    nav_items = [
        # General section (without title for cleaner look)
        NavItem(label='Inicio', path='/', icon='home'),
        NavItem(label='Leads', path='/leads', icon='people'),

        # Auth section with grouping
        {
            'section': 'Autenticación',
            'items': [
                NavItem(label='Usuarios', path='/usuarios', icon='person'),
                NavItem(label='Roles', path='/roles', icon='admin_panel_settings'),
                NavItem(label='Permisos', path='/permisos', icon='vpn_key'),
            ]
        },

        # Infrastructure section for iSeries management
        {
            'section': 'Infraestructura',
            'items': [
                NavItem(label='Empresas', path='/empresas', icon='business'),
                NavItem(label='Configuraciones', path='/configuraciones', icon='settings'),
                NavItem(label='Servidores', path='/servidores', icon='dns'),
                NavItem(label='LPARs', path='/lpars', icon='developer_board'),
                NavItem(label='Réplicas', path='/replicas', icon='sync'),
            ]
        },

        # AI Assistant section
        {
            'section': 'Asistente IA',
            'items': [
                NavItem(label='Chat Base de Datos', path='/chat-db', icon='chat'),
            ]
        }
    ]

    nav_drawer = NavigationDrawer(
        title='',  # No title for minimalism
        width=NAVIGATION['drawer_width'],  # Use design system width
        bg_color='bg-white border-r border-gray-200',
        text_color='text-gray-700',
        hover_color='hover:bg-cyan-50 hover:text-cyan-700',
        nav_items=nav_items,
        value=True  # Start open to show the drawer
    )
    drawer = nav_drawer.create()
    _drawer_instance = nav_drawer

    # Create header component with modern design
    header = AppHeader(
        title='Sinaptrix',
        on_menu_click=nav_drawer.toggle,
        show_menu_button=True
    )
    header_element = header.create()

    # Header without any additional actions - clean and minimal

    # Main container with proper spacing
    with ui.column().classes('w-full min-h-screen flex'):
        # Breadcrumb section with modern styling
        if show_breadcrumb and breadcrumb_items:
            with ui.row().classes('w-full bg-white border-b border-gray-200 px-6 py-2 items-center gap-2'):
                # Home icon
                with ui.link(target='/').classes('text-gray-500 hover:text-cyan-600 transition-colors'):
                    ui.icon('home', size='sm')

                # Breadcrumb items with better styling
                for i, (label, path) in enumerate(breadcrumb_items):
                    ui.icon('chevron_right', size='sm').classes('text-gray-400')
                    if i == len(breadcrumb_items) - 1:
                        # Last item (current page) - no link, highlighted
                        ui.label(label).classes('text-cyan-700 text-sm font-semibold')
                    else:
                        # Intermediate items - with link
                        ui.link(label, path).classes(
                            'text-gray-600 hover:text-cyan-600 text-sm no-underline transition-colors'
                        )

        # Main Content Area with modern background gradient
        with ui.column().classes('w-full flex-grow p-4 md:p-6 items-center bg-gradient-to-br from-gray-50 to-gray-100'):
            # Max width container for content with padding
            with ui.column().classes('w-full max-w-7xl'):
                # Yield control to the actual page content
                yield

    # Create modern footer
    footer = AppFooter(
        text='Sinaptrix',
        version='v2.0',
        show_year=True,
        show_links=True,
        links=[
            {'label': 'Soporte', 'url': '#'},
            {'label': 'Documentación', 'url': '#'}
        ],
        bg_color='bg-gradient-to-r from-gray-800 to-gray-900',
        text_color='text-gray-400'
    )
    footer.create()


@contextmanager
def simple_layout(page_title: str):
    """Simple layout without navigation for login/error pages."""
    ui.page_title(f'SinaptrixOne - {page_title}')

    # Configure page style
    ui.query('body').style('margin: 0; padding: 0')

    # Simple header
    with ui.header().classes('bg-slate-700 text-white shadow-md items-center justify-center'):
        ui.label('SinaptrixOne').classes('text-xl font-bold')

    # Main content centered
    with ui.column().classes('w-full min-h-screen flex items-center justify-center bg-slate-100 p-4'):
        with ui.card().classes('w-full max-w-md'):
            # Page title
            ui.label(page_title).classes('text-2xl font-bold text-center mb-4')

            # Yield control to page content
            yield

    # Simple footer
    from src.ui.components.footer import SimpleFooter
    SimpleFooter('© 2024 SinaptrixOne').create()


# Dashboard layout removed - no longer needed
# @contextmanager
# def dashboard_layout():
#     """Special layout for dashboard with minimal chrome."""
#     pass
