"""Footer component for the application."""
from typing import List, Optional
from datetime import datetime
from nicegui import ui


class AppFooter:
    """Application footer component."""

    def __init__(
        self,
        text: str = 'Powered by FastAPI + NiceGUI',
        version: Optional[str] = 'v1.0',
        bg_color: str = 'bg-slate-700',
        text_color: str = 'text-slate-300',
        show_year: bool = False,
        show_links: bool = False,
        links: Optional[List[dict]] = None
    ):
        """
        Initialize the footer component.

        Args:
            text: Main footer text
            version: Version string to display
            bg_color: Background color class (Tailwind CSS)
            text_color: Text color class (Tailwind CSS)
            show_year: Whether to show the current year
            show_links: Whether to show footer links
            links: List of link dictionaries with 'label' and 'url' keys
        """
        self.text = text
        self.version = version
        self.bg_color = bg_color
        self.text_color = text_color
        self.show_year = show_year
        self.show_links = show_links
        self.links = links or []
        self.footer = None

    def create(self) -> ui.footer:
        """Create and return the footer component."""
        with ui.footer().classes(f'{self.bg_color} {self.text_color} p-4') as self.footer:
            # Main container
            with ui.column().classes('w-full items-center gap-2'):
                # Links section (if enabled)
                if self.show_links and self.links:
                    with ui.row().classes('gap-4 text-sm'):
                        for link in self.links:
                            self._create_link(link)

                # Main footer text with version
                with ui.row().classes('items-center gap-2 text-xs'):
                    # Copyright year if enabled
                    if self.show_year:
                        ui.label(f'© {datetime.now().year}').classes('opacity-75')

                    # Main text
                    ui.label(self.text)

                    # Version if provided
                    if self.version:
                        ui.label(f'| {self.version}').classes('opacity-75')

        return self.footer

    def _create_link(self, link: dict):
        """
        Create a footer link.

        Args:
            link: Dictionary with 'label' and 'url' keys
        """
        ui.link(
            link.get('label', ''),
            link.get('url', '#')
        ).classes(f'{self.text_color} hover:text-white no-underline text-sm')

    def add_social_links(self, social_links: List[dict]):
        """
        Add social media links to the footer.

        Args:
            social_links: List of dictionaries with 'icon' and 'url' keys
        """
        if self.footer:
            with self.footer:
                with ui.row().classes('gap-3 mt-2'):
                    for social in social_links:
                        with ui.link(
                            target=social.get('url', '#')
                        ).classes(f'{self.text_color} hover:text-white'):
                            ui.icon(social.get('icon', 'link')).classes('text-lg')

    def update_text(self, new_text: str):
        """
        Update the footer text dynamically.

        Args:
            new_text: New text to display
        """
        self.text = new_text
        # Note: Dynamic update would require storing element references


class SimpleFooter:
    """Simplified footer component for minimal layouts."""

    def __init__(self, text: str = 'SinaptrixOne'):
        """
        Initialize a simple footer.

        Args:
            text: Text to display in the footer
        """
        self.text = text

    def create(self) -> ui.footer:
        """Create and return a simple footer."""
        with ui.footer().classes('bg-slate-700 text-slate-300 p-2 text-center text-xs') as footer:
            ui.label(self.text)
        return footer
