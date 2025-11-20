"""Reusable confirmation dialog component for NiceGUI."""
from typing import Optional, Callable
from nicegui import ui


class ConfirmDialog:
    """
    Reusable confirmation dialog component.

    Example usage:
        # Basic usage
        confirm = ConfirmDialog(
            title="Confirm Delete",
            message="Are you sure you want to delete this item?",
            on_confirm=lambda: delete_item(item_id)
        )
        confirm.open()

        # With custom styling
        confirm = ConfirmDialog(
            title="Warning",
            message="This action cannot be undone!",
            confirm_text="Yes, proceed",
            cancel_text="No, go back",
            confirm_color="negative",
            icon="warning"
        )
    """

    def __init__(
        self,
        title: str = "Confirmar",
        message: str = "¿Estás seguro?",
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        confirm_text: str = "Confirmar",
        cancel_text: str = "Cancelar",
        confirm_color: str = "primary",
        cancel_color: str = "flat",
        icon: Optional[str] = None,
        icon_color: Optional[str] = None,
        width: str = 'w-96',
        show_close_button: bool = True
    ):
        """
        Initialize ConfirmDialog component.

        Args:
            title: Dialog title
            message: Confirmation message
            on_confirm: Callback when confirmed
            on_cancel: Callback when cancelled
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            confirm_color: Color for confirm button (primary, negative, positive, etc.)
            cancel_color: Color for cancel button
            icon: Optional icon to display
            icon_color: Color for icon
            width: Dialog width class
            show_close_button: Whether to show X close button
        """
        self.title = title
        self.message = message
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.confirm_color = confirm_color
        self.cancel_color = cancel_color
        self.icon = icon
        self.icon_color = icon_color
        self.width = width
        self.show_close_button = show_close_button

        self.dialog = None
        self._create_dialog()

    def _create_dialog(self):
        """Create the dialog structure."""
        self.dialog = ui.dialog()

        with self.dialog:
            with ui.card().classes(self.width):
                # Header with optional close button
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(self.title).classes('text-xl font-semibold')
                    if self.show_close_button:
                        ui.button(
                            icon='close',
                            on_click=self._handle_cancel
                        ).props('flat round dense')

                # Content area
                with ui.row().classes('w-full gap-4 my-4 items-start'):
                    # Optional icon
                    if self.icon:
                        icon_classes = 'text-3xl'
                        if self.icon_color:
                            icon_classes += f' text-{self.icon_color}-600'
                        ui.icon(self.icon, size='lg').classes(icon_classes)

                    # Message
                    ui.label(self.message).classes('text-gray-700 flex-1')

                # Action buttons
                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button(
                        self.cancel_text,
                        on_click=self._handle_cancel
                    ).props(self.cancel_color)

                    ui.button(
                        self.confirm_text,
                        on_click=self._handle_confirm
                    ).props(f'color={self.confirm_color}')

    async def _handle_confirm(self):
        """Handle confirm action."""
        self.dialog.close()

        if self.on_confirm:
            if asyncio.iscoroutinefunction(self.on_confirm):
                await self.on_confirm()
            else:
                self.on_confirm()

    async def _handle_cancel(self):
        """Handle cancel action."""
        self.dialog.close()

        if self.on_cancel:
            if asyncio.iscoroutinefunction(self.on_cancel):
                await self.on_cancel()
            else:
                self.on_cancel()

    def open(self):
        """Open the confirmation dialog."""
        if self.dialog:
            self.dialog.open()

    def close(self):
        """Close the dialog."""
        if self.dialog:
            self.dialog.close()

    @staticmethod
    def ask(
        title: str = "Confirmar",
        message: str = "¿Estás seguro?",
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        **kwargs
    ):
        """
        Static method to quickly show a confirmation dialog.

        Example:
            ConfirmDialog.ask(
                title="Delete Item",
                message="This action cannot be undone!",
                on_confirm=lambda: delete_item(id)
            )
        """
        dialog = ConfirmDialog(
            title=title,
            message=message,
            on_confirm=on_confirm,
            on_cancel=on_cancel,
            **kwargs
        )
        dialog.open()
        return dialog


class AlertDialog:
    """
    Simple alert dialog for notifications.

    Example usage:
        AlertDialog.show(
            title="Success",
            message="Operation completed successfully!",
            type="success"
        )
    """

    @staticmethod
    def show(
        title: str = "Alerta",
        message: str = "",
        type: str = "info",  # info, success, warning, error
        button_text: str = "OK",
        on_close: Optional[Callable] = None,
        width: str = 'w-96'
    ):
        """
        Show an alert dialog.

        Args:
            title: Alert title
            message: Alert message
            type: Alert type (info, success, warning, error)
            button_text: Text for close button
            on_close: Callback when closed
            width: Dialog width
        """
        # Type configurations
        type_config = {
            'info': {'icon': 'info', 'color': 'blue'},
            'success': {'icon': 'check_circle', 'color': 'green'},
            'warning': {'icon': 'warning', 'color': 'orange'},
            'error': {'icon': 'error', 'color': 'red'}
        }

        config = type_config.get(type, type_config['info'])

        with ui.dialog() as dialog, ui.card().classes(width):
            # Header
            with ui.row().classes('w-full items-center gap-3'):
                ui.icon(config['icon'], size='lg').classes(f'text-{config["color"]}-600')
                ui.label(title).classes('text-xl font-semibold flex-1')

            # Message
            if message:
                ui.label(message).classes('text-gray-700 mt-4')

            # Close button
            with ui.row().classes('w-full justify-end mt-4'):
                async def handle_close():
                    dialog.close()
                    if on_close:
                        if asyncio.iscoroutinefunction(on_close):
                            await on_close()
                        else:
                            on_close()

                ui.button(button_text, on_click=handle_close).props('color=primary')

        dialog.open()
        return dialog


import asyncio