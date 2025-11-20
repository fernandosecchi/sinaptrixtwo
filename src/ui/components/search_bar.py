"""Reusable search bar component for NiceGUI."""
from typing import Optional, Callable
from nicegui import ui


class SearchBar:
    """
    Reusable search bar component with search and clear functionality.

    Example usage:
        search_bar = SearchBar(
            placeholder="Search users...",
            on_search=lambda value: load_data(value),
            on_clear=lambda: load_data()
        )
    """

    def __init__(
        self,
        placeholder: str = "Search...",
        on_search: Optional[Callable] = None,
        on_clear: Optional[Callable] = None,
        container_classes: str = 'w-full gap-4 items-center',
        input_classes: str = 'flex-1',
        show_clear_button: bool = True,
        search_on_enter: bool = True,
        search_button_text: str = 'Buscar',
        clear_button_text: str = 'Limpiar',
        search_icon: str = 'search',
        clear_icon: str = 'clear'
    ):
        """
        Initialize SearchBar component.

        Args:
            placeholder: Placeholder text for input
            on_search: Callback function when search is triggered
            on_clear: Callback function when clear is triggered
            container_classes: CSS classes for container
            input_classes: CSS classes for input field
            show_clear_button: Whether to show clear button
            search_on_enter: Whether to trigger search on Enter key
            search_button_text: Text for search button
            clear_button_text: Text for clear button
            search_icon: Icon for search button
            clear_icon: Icon for clear button
        """
        self.placeholder = placeholder
        self.on_search = on_search
        self.on_clear = on_clear
        self.container_classes = container_classes
        self.input_classes = input_classes
        self.show_clear_button = show_clear_button
        self.search_on_enter = search_on_enter
        self.search_button_text = search_button_text
        self.clear_button_text = clear_button_text
        self.search_icon = search_icon
        self.clear_icon = clear_icon

        self.input = None
        self.container = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        self.container = ui.row().classes(self.container_classes)

        with self.container:
            # Search input
            self.input = ui.input(
                placeholder=self.placeholder
            ).props('outlined dense clearable').classes(self.input_classes)

            # Search handler
            async def perform_search():
                if self.on_search:
                    if asyncio.iscoroutinefunction(self.on_search):
                        await self.on_search(self.input.value)
                    else:
                        self.on_search(self.input.value)

            # Clear handler
            async def perform_clear():
                self.input.value = ''
                if self.on_clear:
                    if asyncio.iscoroutinefunction(self.on_clear):
                        await self.on_clear()
                    else:
                        self.on_clear()

            # Search button
            if self.search_button_text:
                ui.button(
                    self.search_button_text,
                    on_click=perform_search,
                    icon=self.search_icon
                ).props('color=primary')
            else:
                # Icon-only button - make it smaller
                ui.button(
                    on_click=perform_search,
                    icon=self.search_icon
                ).props('color=primary size=sm dense')

            # Clear button
            if self.show_clear_button:
                if self.clear_button_text:
                    ui.button(
                        self.clear_button_text,
                        on_click=perform_clear,
                        icon=self.clear_icon
                    ).props('flat')
                else:
                    # Icon-only button - make it smaller
                    ui.button(
                        on_click=perform_clear,
                        icon=self.clear_icon
                    ).props('flat size=sm dense')

            # Enter key handler
            if self.search_on_enter:
                self.input.on('keydown.enter', perform_search)

    def get_value(self) -> str:
        """Get current search value."""
        return self.input.value if self.input else ''

    def set_value(self, value: str):
        """Set search value."""
        if self.input:
            self.input.value = value

    def clear(self):
        """Clear search input."""
        if self.input:
            self.input.value = ''

    def focus(self):
        """Focus the search input."""
        if self.input:
            self.input.focus()

    def disable(self):
        """Disable the search bar."""
        if self.input:
            self.input.disable()

    def enable(self):
        """Enable the search bar."""
        if self.input:
            self.input.enable()


import asyncio