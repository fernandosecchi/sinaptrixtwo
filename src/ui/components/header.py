"""Header component for the application."""
from typing import Optional, Callable
from nicegui import ui, app


class AppHeader:
    """Modern application header component with gradient design."""

    def __init__(
        self,
        title: str = 'Sinaptrix',
        on_menu_click: Optional[Callable] = None,
        bg_color: str = 'bg-gradient-to-r from-cyan-600 to-cyan-700',
        text_color: str = 'text-white',
        show_menu_button: bool = True
    ):
        """
        Initialize the header component.

        Args:
            title: The application title to display
            on_menu_click: Callback function when menu button is clicked
            bg_color: Background color class (Tailwind CSS)
            text_color: Text color class (Tailwind CSS)
            show_menu_button: Whether to show the menu toggle button
        """
        self.title = title
        self.on_menu_click = on_menu_click
        self.bg_color = bg_color
        self.text_color = text_color
        self.show_menu_button = show_menu_button
        self.header = None

    def create(self) -> ui.header:
        """Create and return the modern header component."""
        with ui.header().classes(f'{self.bg_color} {self.text_color} shadow-lg h-16 px-4') as self.header:
            with ui.row().classes('w-full items-center h-full'):
                # Menu toggle button with hover effect
                if self.show_menu_button and self.on_menu_click:
                    ui.button(
                        on_click=self.on_menu_click,
                        icon='menu'
                    ).props('flat color=white round').classes('hover:bg-white/20 transition-colors')

                # Title section
                with ui.row().classes('items-center ml-2'):
                    # Title with better typography
                    ui.label(self.title).classes('text-xl font-semibold tracking-tight')

                # Spacer to push content to the right
                ui.space()

                # User section with modern styling
                if app.storage.user.get('authenticated'):
                    username = app.storage.user.get('username', 'Usuario')

                    with ui.row().classes('items-center gap-3'):
                        # User chip with avatar
                        with ui.row().classes('items-center gap-2 bg-white/10 backdrop-blur rounded-full px-3 py-1.5'):
                            ui.icon('person', size='sm').classes('text-cyan-100')
                            ui.label(username).classes('text-sm font-medium text-white')

                        # Actions dropdown menu
                        with ui.button(icon='more_vert').props('flat color=white round size=sm').classes('hover:bg-white/20'):
                            with ui.menu().classes('min-w-48') as menu:
                                ui.menu_item(
                                    'Mi Perfil',
                                    on_click=lambda: ui.notify('Perfil', type='info')
                                ).props('icon=person')
                                ui.menu_item(
                                    'Configuración',
                                    on_click=lambda: ui.notify('Configuración', type='info')
                                ).props('icon=settings')
                                ui.separator()
                                ui.menu_item(
                                    'Cerrar Sesión',
                                    on_click=lambda: ui.navigate.to('/logout')
                                ).props('icon=logout text-color=red')

        return self.header

    def add_action(self, icon: str, tooltip: str, on_click: Callable) -> ui.button:
        """
        Add an action button to the header (on the right side).

        Args:
            icon: Material icon name
            tooltip: Tooltip text for the button
            on_click: Callback function when clicked

        Returns:
            The created button element
        """
        if self.header:
            with self.header:
                btn = ui.button(icon=icon, on_click=on_click).props('flat color=white')
                if tooltip:
                    btn.tooltip(tooltip)
                return btn
        raise RuntimeError("Header must be created first before adding actions")

    def update_title(self, new_title: str):
        """Update the header title dynamically."""
        self.title = new_title
        # Note: This would require storing a reference to the label element
        # For simplicity, this is left as a future enhancement
