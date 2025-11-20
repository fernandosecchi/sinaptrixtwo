"""Reusable stats card component for NiceGUI."""
from typing import Optional, Union
from nicegui import ui


class StatsCard:
    """
    Reusable stats card component for displaying metrics.

    Example usage:
        stats_card = StatsCard(
            title="Total Users",
            value=150,
            subtitle="Active users this month",
            icon="people",
            color="blue",
            trend_value=12.5,
            trend_direction="up"
        )
    """

    def __init__(
        self,
        title: str = "",
        value: Union[str, int, float] = 0,
        subtitle: Optional[str] = None,
        icon: Optional[str] = None,
        color: str = 'blue',
        trend_value: Optional[float] = None,
        trend_direction: Optional[str] = None,  # 'up' or 'down'
        format_value: Optional[str] = None,  # e.g., "{:.1f}%" or "${:,.2f}"
        container_classes: str = 'flex-1',
        clickable: bool = False,
        on_click: Optional[callable] = None
    ):
        """
        Initialize StatsCard component.

        Args:
            title: Card title
            value: Main value to display
            subtitle: Subtitle text
            icon: Icon name
            color: Color theme (blue, green, red, orange, purple, etc.)
            trend_value: Trend percentage value
            trend_direction: Direction of trend ('up' or 'down')
            format_value: Format string for value
            container_classes: CSS classes for container
            clickable: Whether card is clickable
            on_click: Callback for click event
        """
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        self.color = color
        self.trend_value = trend_value
        self.trend_direction = trend_direction
        self.format_value = format_value
        self.container_classes = container_classes
        self.clickable = clickable
        self.on_click = on_click

        self.card = None
        self.value_label = None
        self.title_label = None
        self.subtitle_label = None
        self.trend_label = None

        self._setup_ui()

    def _get_color_classes(self) -> dict:
        """Get color classes based on color theme."""
        color_map = {
            'blue': {
                'bg': 'bg-blue-50',
                'text': 'text-blue-600',
                'icon': 'text-blue-500',
                'hover': 'hover:bg-blue-100'
            },
            'green': {
                'bg': 'bg-green-50',
                'text': 'text-green-600',
                'icon': 'text-green-500',
                'hover': 'hover:bg-green-100'
            },
            'red': {
                'bg': 'bg-red-50',
                'text': 'text-red-600',
                'icon': 'text-red-500',
                'hover': 'hover:bg-red-100'
            },
            'orange': {
                'bg': 'bg-orange-50',
                'text': 'text-orange-600',
                'icon': 'text-orange-500',
                'hover': 'hover:bg-orange-100'
            },
            'purple': {
                'bg': 'bg-purple-50',
                'text': 'text-purple-600',
                'icon': 'text-purple-500',
                'hover': 'hover:bg-purple-100'
            },
            'gray': {
                'bg': 'bg-gray-50',
                'text': 'text-gray-600',
                'icon': 'text-gray-500',
                'hover': 'hover:bg-gray-100'
            }
        }
        return color_map.get(self.color, color_map['blue'])

    def _format_value(self, value: Union[str, int, float]) -> str:
        """Format the value based on format string."""
        if self.format_value and isinstance(value, (int, float)):
            return self.format_value.format(value)
        return str(value)

    def _setup_ui(self):
        """Setup the UI components."""
        colors = self._get_color_classes()

        # Create card
        card_classes = f'{self.container_classes} p-6 {colors["bg"]} rounded-lg'
        if self.clickable:
            card_classes += f' cursor-pointer {colors["hover"]} transition-colors'

        self.card = ui.card().classes(card_classes)

        if self.clickable and self.on_click:
            self.card.on('click', self.on_click)

        with self.card:
            # Top row with icon and trend
            with ui.row().classes('w-full items-start justify-between'):
                # Icon
                if self.icon:
                    with ui.element('div').classes(f'p-3 rounded-full bg-white shadow-sm'):
                        ui.icon(self.icon, size='lg').classes(colors['icon'])

                # Trend indicator
                if self.trend_value is not None and self.trend_direction:
                    trend_color = 'text-green-600' if self.trend_direction == 'up' else 'text-red-600'
                    trend_icon = 'trending_up' if self.trend_direction == 'up' else 'trending_down'

                    with ui.row().classes('items-center gap-1'):
                        ui.icon(trend_icon, size='sm').classes(trend_color)
                        self.trend_label = ui.label(f'{self.trend_value:+.1f}%').classes(f'text-sm font-semibold {trend_color}')

            # Main content
            with ui.column().classes('gap-2 mt-4'):
                # Title
                if self.title:
                    self.title_label = ui.label(self.title).classes('text-sm text-gray-600 uppercase tracking-wide')

                # Value
                self.value_label = ui.label(self._format_value(self.value)).classes(f'text-3xl font-bold {colors["text"]}')

                # Subtitle
                if self.subtitle:
                    self.subtitle_label = ui.label(self.subtitle).classes('text-sm text-gray-500 mt-1')

    def update_value(self, value: Union[str, int, float], animate: bool = True):
        """
        Update the card value.

        Args:
            value: New value
            animate: Whether to animate the change
        """
        self.value = value
        if self.value_label:
            self.value_label.text = self._format_value(value)

            # Optional: Add animation effect
            if animate:
                self.value_label.classes(add='animate-pulse')
                ui.timer(1.0, lambda: self.value_label.classes(remove='animate-pulse'), once=True)

    def update_trend(self, value: float, direction: str):
        """
        Update trend indicator.

        Args:
            value: Trend value
            direction: 'up' or 'down'
        """
        self.trend_value = value
        self.trend_direction = direction

        if self.trend_label:
            self.trend_label.text = f'{value:+.1f}%'
            trend_color = 'text-green-600' if direction == 'up' else 'text-red-600'
            self.trend_label.classes(replace=f'text-sm font-semibold {trend_color}')

    def update_subtitle(self, subtitle: str):
        """Update subtitle text."""
        self.subtitle = subtitle
        if self.subtitle_label:
            self.subtitle_label.text = subtitle

    def hide(self):
        """Hide the stats card."""
        if self.card:
            self.card.visible = False

    def show(self):
        """Show the stats card."""
        if self.card:
            self.card.visible = True


class StatsGrid:
    """
    Container for multiple stats cards in a grid layout.

    Example usage:
        stats_grid = StatsGrid()
        stats_grid.add_card(StatsCard(title="Users", value=150))
        stats_grid.add_card(StatsCard(title="Sales", value=45000, format_value="${:,.0f}"))
    """

    def __init__(
        self,
        columns: int = 4,
        gap: str = 'gap-4',
        container_classes: str = 'w-full'
    ):
        """
        Initialize StatsGrid.

        Args:
            columns: Number of columns in grid
            gap: Gap between cards
            container_classes: CSS classes for container
        """
        self.columns = columns
        self.gap = gap
        self.container_classes = container_classes
        self.cards = []

        self.container = ui.row().classes(f'{container_classes} {gap}')

    def add_card(self, card: StatsCard):
        """Add a stats card to the grid."""
        self.cards.append(card)
        return card

    def clear(self):
        """Clear all cards from the grid."""
        self.container.clear()
        self.cards = []

    def create_card(self, **kwargs) -> StatsCard:
        """Create and add a new stats card."""
        card = StatsCard(**kwargs)
        self.add_card(card)
        return card