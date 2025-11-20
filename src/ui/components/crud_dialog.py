"""Reusable CRUD dialog component for NiceGUI."""
from typing import Optional, Callable, Dict, Any, List
from enum import Enum
from nicegui import ui


class DialogMode(Enum):
    """Dialog operation modes."""
    CREATE = "create"
    EDIT = "edit"
    VIEW = "view"


class FormField:
    """Configuration for a form field."""

    def __init__(
        self,
        name: str,
        label: str,
        field_type: str = 'text',
        required: bool = False,
        placeholder: str = '',
        options: Optional[Dict[str, str]] = None,
        default_value: Any = None,
        readonly_in_edit: bool = False,
        full_width: bool = True,
        validation_fn: Optional[Callable] = None
    ):
        """
        Initialize FormField configuration.

        Args:
            name: Field name (key in data dict)
            label: Display label
            field_type: Type of input (text, email, number, select, textarea, checkbox)
            required: Whether field is required
            placeholder: Placeholder text
            options: Options for select fields
            default_value: Default value for new records
            readonly_in_edit: Whether field is readonly in edit mode
            full_width: Whether field takes full width
            validation_fn: Optional validation function
        """
        self.name = name
        self.label = label
        self.field_type = field_type
        self.required = required
        self.placeholder = placeholder
        self.options = options or {}
        self.default_value = default_value
        self.readonly_in_edit = readonly_in_edit
        self.full_width = full_width
        self.validation_fn = validation_fn


class CrudDialog:
    """
    Reusable CRUD dialog component.

    Example usage:
        dialog = CrudDialog(
            title="User Management",
            fields=[
                FormField('name', 'Name', required=True),
                FormField('email', 'Email', field_type='email', required=True),
                FormField('role', 'Role', field_type='select', options={
                    'admin': 'Administrator',
                    'user': 'User'
                }),
            ],
            on_save=lambda data, mode: save_user(data, mode),
            on_delete=lambda data: delete_user(data['id'])
        )

        # Open for create
        dialog.open(DialogMode.CREATE)

        # Open for edit
        dialog.open(DialogMode.EDIT, existing_data)
    """

    def __init__(
        self,
        title: str = "Form",
        fields: List[FormField] = None,
        on_save: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        width: str = 'w-96',
        show_delete_in_edit: bool = True,
        save_button_text: Dict[DialogMode, str] = None,
        cancel_button_text: str = 'Cancelar'
    ):
        """
        Initialize CrudDialog component.

        Args:
            title: Dialog title
            fields: List of form fields
            on_save: Callback for save action (receives data dict and mode)
            on_delete: Callback for delete action
            width: Dialog width class
            show_delete_in_edit: Whether to show delete button in edit mode
            save_button_text: Text for save button per mode
            cancel_button_text: Text for cancel button
        """
        self.title = title
        self.fields = fields or []
        self.on_save = on_save
        self.on_delete = on_delete
        self.width = width
        self.show_delete_in_edit = show_delete_in_edit
        self.save_button_text = save_button_text or {
            DialogMode.CREATE: 'Guardar',
            DialogMode.EDIT: 'Actualizar',
            DialogMode.VIEW: 'Cerrar'
        }
        self.cancel_button_text = cancel_button_text

        self.dialog = None
        self.form_inputs = {}
        self.current_mode = DialogMode.CREATE
        self.current_data = {}

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        self.dialog = ui.dialog()

        with self.dialog:
            with ui.card().classes(self.width):
                # Title
                self.title_label = ui.label(self.title).classes('text-xl font-semibold')

                # Form container
                self.form_container = ui.column().classes('w-full gap-4')

                # Action buttons
                self.actions_container = ui.row().classes('w-full justify-end gap-2 mt-4')

    def _render_form(self):
        """Render form fields based on current mode."""
        self.form_container.clear()
        self.form_inputs = {}

        with self.form_container:
            # Group fields by row (side by side for non-full-width fields)
            row_container = None

            for field in self.fields:
                # Create new row if needed
                if field.full_width or row_container is None:
                    row_container = ui.row().classes('w-full gap-2')

                with row_container:
                    # Container for field
                    field_container = ui.element('div')
                    if field.full_width:
                        field_container.classes('w-full')
                    else:
                        field_container.classes('flex-1')

                    with field_container:
                        # Create appropriate input based on field type
                        if field.field_type == 'select':
                            input_widget = ui.select(
                                field.options,
                                label=field.label + ('*' if field.required else ''),
                                value=self.current_data.get(field.name, field.default_value)
                            ).props('outlined dense').classes('w-full')

                        elif field.field_type == 'textarea':
                            input_widget = ui.textarea(
                                label=field.label + ('*' if field.required else ''),
                                value=self.current_data.get(field.name, field.default_value or ''),
                                placeholder=field.placeholder
                            ).props('outlined dense').classes('w-full')

                        elif field.field_type == 'checkbox':
                            input_widget = ui.checkbox(
                                field.label,
                                value=self.current_data.get(field.name, field.default_value or False)
                            )

                        elif field.field_type == 'number':
                            input_widget = ui.number(
                                label=field.label + ('*' if field.required else ''),
                                value=self.current_data.get(field.name, field.default_value),
                                placeholder=field.placeholder
                            ).props('outlined dense').classes('w-full')

                        else:  # text, email, etc.
                            input_widget = ui.input(
                                label=field.label + ('*' if field.required else ''),
                                value=self.current_data.get(field.name, field.default_value or ''),
                                placeholder=field.placeholder
                            ).props('outlined dense').classes('w-full')

                            # Add specific input type
                            if field.field_type == 'email':
                                input_widget.props('type=email')

                        # Handle readonly state
                        if self.current_mode == DialogMode.VIEW:
                            input_widget.disable()
                        elif self.current_mode == DialogMode.EDIT and field.readonly_in_edit:
                            input_widget.disable()

                        # Store reference
                        self.form_inputs[field.name] = input_widget

                # Reset row container for full-width fields
                if field.full_width:
                    row_container = None

    def _render_actions(self):
        """Render action buttons based on current mode."""
        self.actions_container.clear()

        with self.actions_container:
            if self.current_mode == DialogMode.VIEW:
                # View mode: only close button
                ui.button(
                    self.save_button_text[DialogMode.VIEW],
                    on_click=self.close
                ).props('color=primary')

            else:
                # Delete button in edit mode
                if self.current_mode == DialogMode.EDIT and self.show_delete_in_edit and self.on_delete:
                    async def confirm_delete():
                        with ui.dialog() as confirm_dialog, ui.card():
                            ui.label('¿Estás seguro de que deseas eliminar este registro?')
                            with ui.row().classes('w-full justify-end gap-2'):
                                ui.button('Cancelar', on_click=confirm_dialog.close).props('flat')

                                async def perform_delete():
                                    confirm_dialog.close()
                                    if asyncio.iscoroutinefunction(self.on_delete):
                                        await self.on_delete(self.current_data)
                                    else:
                                        self.on_delete(self.current_data)
                                    self.close()

                                ui.button('Eliminar', on_click=perform_delete).props('color=negative')
                        confirm_dialog.open()

                    ui.button(
                        'Eliminar',
                        on_click=confirm_delete,
                        icon='delete'
                    ).props('color=negative flat')

                # Cancel button
                ui.button(
                    self.cancel_button_text,
                    on_click=self.close
                ).props('flat')

                # Save button
                async def save_data():
                    # Collect form data
                    form_data = {}
                    errors = []

                    for field in self.fields:
                        input_widget = self.form_inputs.get(field.name)
                        if input_widget:
                            value = input_widget.value

                            # Validation
                            if field.required and not value:
                                errors.append(f'{field.label} es requerido')

                            if field.validation_fn and value:
                                error = field.validation_fn(value)
                                if error:
                                    errors.append(error)

                            form_data[field.name] = value

                    # Show errors if any
                    if errors:
                        ui.notify('\n'.join(errors), type='warning')
                        return

                    # Include existing data (for fields not in form)
                    for key, value in self.current_data.items():
                        if key not in form_data:
                            form_data[key] = value

                    # Call save callback
                    if self.on_save:
                        try:
                            if asyncio.iscoroutinefunction(self.on_save):
                                await self.on_save(form_data, self.current_mode)
                            else:
                                self.on_save(form_data, self.current_mode)
                            self.close()
                        except Exception as e:
                            ui.notify(f'Error: {e}', type='negative')

                ui.button(
                    self.save_button_text[self.current_mode],
                    on_click=save_data
                ).props('color=primary')

    def open(self, mode: DialogMode = DialogMode.CREATE, data: Optional[Dict[str, Any]] = None):
        """
        Open the dialog in specified mode.

        Args:
            mode: Dialog mode (CREATE, EDIT, VIEW)
            data: Existing data for edit/view modes
        """
        self.current_mode = mode
        self.current_data = data or {}

        # Update title based on mode
        mode_prefix = {
            DialogMode.CREATE: 'Crear',
            DialogMode.EDIT: 'Editar',
            DialogMode.VIEW: 'Ver'
        }
        self.title_label.text = f'{mode_prefix[mode]} {self.title}'

        # Render form and actions
        self._render_form()
        self._render_actions()

        # Open dialog
        self.dialog.open()

    def close(self):
        """Close the dialog."""
        if self.dialog:
            self.dialog.close()

    def clear(self):
        """Clear form data."""
        self.current_data = {}
        for input_widget in self.form_inputs.values():
            if hasattr(input_widget, 'value'):
                input_widget.value = ''


import asyncio