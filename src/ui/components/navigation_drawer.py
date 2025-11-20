"""Navigation drawer component for the application."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from nicegui import ui


@dataclass
class NavItem:
    """Navigation item configuration."""
    label: str
    path: str
    icon: Optional[str] = None
    badge: Optional[str] = None
    children: Optional[List['NavItem']] = None


class NavigationDrawer:
    """Side navigation drawer component."""

    def __init__(
        self,
        title: str = 'Navegación',
        width: str = '200px',
        bg_color: str = 'bg-slate-200',
        text_color: str = 'text-slate-700',
        hover_color: str = 'hover:bg-slate-300',
        nav_items: Optional[List[NavItem]] = None,
        value: bool = True
    ):
        """
        Initialize the navigation drawer component.

        Args:
            title: Title displayed at the top of the drawer
            width: Width of the drawer in pixels (e.g., '200px', '150px')
            bg_color: Background color class (Tailwind CSS)
            text_color: Text color class (Tailwind CSS)
            hover_color: Hover color class (Tailwind CSS)
            nav_items: List of navigation items
            value: Initial open/closed state (True = open)
        """
        self.title = title
        self.width = width
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.nav_items = nav_items or self._get_default_items()
        self.value = value
        self.drawer = None

    def _get_default_items(self) -> List[NavItem]:
        """Get default navigation items."""
        return [
            NavItem(label='Inicio', path='/', icon='home'),
            NavItem(label='Leads', path='/leads', icon='people'),
            NavItem(label='Usuarios', path='/usuarios', icon='person'),
            NavItem(label='Roles', path='/roles', icon='badge')
        ]

    def create(self) -> ui.left_drawer:
        """Create and return the navigation drawer component."""
        # Extract numeric width value for props
        width_value = self.width.replace('px', '')

        # Create drawer with specified width
        # Use persistent to keep it always visible and fixed width
        drawer_props = f'width={width_value} persistent'

        with ui.left_drawer(value=self.value).classes(self.bg_color).props(drawer_props) as self.drawer:
            # Apply explicit width styling to ensure it respects the configured width
            self.drawer.style(f'width: {self.width} !important; min-width: {self.width} !important; max-width: {self.width} !important')

            # Title section (optional)
            if self.title:
                ui.label(self.title).classes(f'text-lg font-bold p-3 {self.text_color}')
                ui.separator()

            # Navigation items with sections
            with ui.column().classes('w-full gap-0'):
                # Process navigation items (could be sections or regular items)
                for item in self.nav_items:
                    if isinstance(item, dict) and 'section' in item:
                        # This is a section with title
                        self._create_section(item['section'], item.get('items', []))
                    else:
                        # Regular navigation item
                        self._create_nav_item(item)

        return self.drawer

    def _create_section(self, title: str, items: List[NavItem]):
        """
        Create a collapsible section with title and grouped items.

        Args:
            title: Section title
            items: List of navigation items in this section
        """
        # Section separator with more spacing
        if title:  # Only add separator if there's a title
            ui.separator().classes('my-3 mx-3')

            # Collapsible section using expansion - start expanded
            with ui.expansion(title, value=True).classes('w-full') as expansion:
                # Style the expansion header with better spacing and colors
                expansion.classes(f'{self.text_color}')
                expansion.props('dense expand-icon-class="text-gray-500"')

                # Custom styling for the header
                expansion.style('margin-bottom: 0.5rem')

                # Add custom CSS for the header text - removed tracking-wider to prevent text overflow
                with expansion:
                    expansion._props['header-class'] = 'text-xs font-semibold uppercase text-gray-600'

                # Section items inside the expansion with spacing
                with ui.column().classes('w-full gap-0.5 pb-2'):
                    for item in items:
                        self._create_nav_item(item)

    def _create_nav_item(self, item: NavItem, indent: int = 0):
        """
        Create a modern navigation item with hover effects.

        Args:
            item: Navigation item configuration
            indent: Indentation level for nested items
        """
        # Calculate if we should use compact mode based on drawer width
        width_pixels = int(self.width.replace('px', ''))
        is_compact = width_pixels < 150  # Use compact mode for narrow drawers

        # Create navigation item with modern styling
        padding_left = f'pl-{3 + (indent * 2)}'

        # Modern styling with transitions
        base_classes = f'w-full {padding_left} pr-3 no-underline flex items-center rounded-lg transition-all duration-150'

        if is_compact:
            # Compact mode - smaller text and padding
            link_classes = f'{base_classes} py-2 gap-2 {self.hover_color} {self.text_color}'
            icon_size = 'sm'
            text_size = 'text-sm'
        else:
            # Normal mode - regular sizing with better spacing
            link_classes = f'{base_classes} py-2.5 gap-3 {self.hover_color} {self.text_color}'
            icon_size = 'md'
            text_size = 'text-sm'

        with ui.link(target=item.path).classes(link_classes):
            # Add icon with color
            if item.icon:
                ui.icon(item.icon, size=icon_size).classes('text-cyan-600')

            # Add label with better typography
            ui.label(item.label).classes(f'flex-grow {text_size} font-medium')

            # Add badge with modern styling if provided
            if item.badge:
                with ui.element('div').classes('bg-red-500 text-white text-xs px-2 py-0.5 rounded-full font-medium'):
                    ui.label(item.badge)

        # Recursively create children if they exist
        if item.children:
            for child in item.children:
                self._create_nav_item(child, indent + 1)

    def toggle(self):
        """Toggle the drawer open/closed state."""
        if self.drawer:
            self.drawer.toggle()

    def open(self):
        """Open the drawer."""
        if self.drawer:
            self.drawer.value = True

    def close(self):
        """Close the drawer."""
        if self.drawer:
            self.drawer.value = False

    def add_item(self, item: NavItem):
        """
        Add a new navigation item dynamically.

        Args:
            item: Navigation item to add
        """
        self.nav_items.append(item)
        # Note: Dynamic updates would require re-rendering the drawer

    def add_separator(self):
        """Add a separator to the navigation drawer."""
        if self.drawer:
            with self.drawer:
                ui.separator().classes('my-2')

    def add_section(self, title: str, items: List[NavItem]):
        """
        Add a new section to the navigation drawer.

        Args:
            title: Section title
            items: List of navigation items for this section
        """
        if self.drawer:
            with self.drawer:
                # Section title
                ui.label(title).classes(f'text-sm font-semibold p-3 pt-4 {self.text_color} opacity-75')

                # Section items
                with ui.column().classes('w-full gap-0'):
                    for item in items:
                        self._create_nav_item(item)
