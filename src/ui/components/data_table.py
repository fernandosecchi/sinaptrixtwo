"""Reusable data table component for NiceGUI."""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from nicegui import ui


@dataclass
class TableColumn:
    """Column configuration for DataTable."""
    name: str
    label: str
    field: str
    sortable: bool = True
    align: str = 'left'
    format_fn: Optional[Callable] = None


class DataTable:
    """
    Reusable data table component with common functionality.

    Example usage:
        table = DataTable(
            title="Users List",
            columns=[
                TableColumn('id', 'ID', 'id'),
                TableColumn('name', 'Name', 'name'),
                TableColumn('email', 'Email', 'email'),
            ],
            on_view=lambda row: show_details(row),
            on_edit=lambda row: edit_item(row),
            on_delete=lambda row: delete_item(row),
            searchable_fields=['name', 'email']
        )

        # Load data
        table.load_data(users_list)
    """

    def __init__(
        self,
        title: str = "",
        columns: List[TableColumn] = None,
        rows_per_page: int = 10,
        on_view: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        searchable_fields: List[str] = None,
        container_classes: str = 'w-full',
        show_stats: bool = True,
        show_actions: bool = True,
        custom_actions_template: Optional[str] = None
    ):
        """
        Initialize DataTable component.

        Args:
            title: Table title
            columns: List of TableColumn configurations
            rows_per_page: Number of rows per page
            on_view: Callback for view action
            on_edit: Callback for edit action
            on_delete: Callback for delete action
            searchable_fields: Fields to search in
            container_classes: CSS classes for container
            show_stats: Whether to show stats card
            show_actions: Whether to show action buttons
            custom_actions_template: Custom template for actions column
        """
        self.title = title
        self.columns = columns or []
        self.rows_per_page = rows_per_page
        self.on_view = on_view
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.searchable_fields = searchable_fields or []
        self.container_classes = container_classes
        self.show_stats = show_stats
        self.show_actions = show_actions
        self.custom_actions_template = custom_actions_template

        self.table = None
        self.container = None
        self.stats_label = None
        self.original_data = []
        self.filtered_data = []

        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components."""
        self.container = ui.column().classes(self.container_classes)

        with self.container:
            # Stats card if enabled
            if self.show_stats:
                with ui.card().classes('w-full p-4 mb-4'):
                    self.stats_label = ui.label('').classes('text-lg')

            # Prepare columns
            table_columns = []
            for col in self.columns:
                table_columns.append({
                    'name': col.name,
                    'label': col.label,
                    'field': col.field,
                    'sortable': col.sortable,
                    'align': col.align,
                })

            # Add actions column if needed
            if self.show_actions:
                table_columns.append({
                    'name': 'actions',
                    'label': 'Acciones',
                    'field': 'actions',
                    'align': 'center'
                })

            # Create table
            self.table = ui.table(
                columns=table_columns,
                rows=[],
                row_key='id',
                title=self.title,
                pagination={'rowsPerPage': self.rows_per_page, 'sortBy': None}
            ).classes('w-full')

            # Add actions slot if enabled
            if self.show_actions:
                if self.custom_actions_template:
                    self.table.add_slot('body-cell-actions', self.custom_actions_template)
                else:
                    # Default actions template
                    actions_template = '''
                        <q-td :props="props" class="text-center">
                    '''

                    if self.on_view:
                        actions_template += '''
                            <q-btn @click="$parent.$emit('view', props.row)" icon="visibility"
                                   color="info" flat dense round size="sm">
                                <q-tooltip>Ver detalles</q-tooltip>
                            </q-btn>
                        '''

                    if self.on_edit:
                        actions_template += '''
                            <q-btn @click="$parent.$emit('edit', props.row)" icon="edit"
                                   color="warning" flat dense round size="sm" class="q-ml-sm">
                                <q-tooltip>Editar</q-tooltip>
                            </q-btn>
                        '''

                    if self.on_delete:
                        actions_template += '''
                            <q-btn @click="$parent.$emit('delete', props.row)" icon="delete"
                                   color="negative" flat dense round size="sm" class="q-ml-sm">
                                <q-tooltip>Eliminar</q-tooltip>
                            </q-btn>
                        '''

                    actions_template += '''
                        </q-td>
                    '''

                    self.table.add_slot('body-cell-actions', actions_template)

                # Setup event handlers
                if self.on_view:
                    self.table.on('view', lambda e: self.on_view(e.args))
                if self.on_edit:
                    self.table.on('edit', lambda e: self.on_edit(e.args))
                if self.on_delete:
                    self.table.on('delete', lambda e: self.on_delete(e.args))

    def load_data(self, data: List[Dict[str, Any]]):
        """
        Load data into the table.

        Args:
            data: List of dictionaries with table data
        """
        self.original_data = data
        self.filtered_data = data

        # Format data according to column configurations
        formatted_rows = []
        for item in data:
            row = {}
            for col in self.columns:
                value = item.get(col.field)
                if col.format_fn:
                    value = col.format_fn(value)
                row[col.field] = value

            # Add id if present
            if 'id' in item:
                row['id'] = item['id']

            # Add any additional fields
            for key, value in item.items():
                if key not in row:
                    row[key] = value

            formatted_rows.append(row)

        # Update table
        self.table.rows = formatted_rows
        self.table.update()

        # Update stats
        if self.show_stats and self.stats_label:
            self.stats_label.text = f'Total de registros: {len(formatted_rows)}'

    def filter_data(self, search_term: str):
        """
        Filter data based on search term.

        Args:
            search_term: String to search for in searchable fields
        """
        if not search_term:
            self.load_data(self.original_data)
            return

        search_lower = search_term.lower()
        filtered = []

        for item in self.original_data:
            for field in self.searchable_fields:
                value = str(item.get(field, '')).lower()
                if search_lower in value:
                    filtered.append(item)
                    break

        self.load_data(filtered)

        # Update stats with filter info
        if self.show_stats and self.stats_label:
            self.stats_label.text = f'Mostrando {len(filtered)} de {len(self.original_data)} registros'

    def refresh(self):
        """Refresh the table display."""
        self.table.update()

    def clear(self):
        """Clear all table data."""
        self.table.rows = []
        self.table.update()
        if self.show_stats and self.stats_label:
            self.stats_label.text = 'Sin datos'

    def get_selected_rows(self) -> List[Dict[str, Any]]:
        """Get selected rows from the table."""
        # This would need to be implemented with table selection features
        return []

    def set_loading(self, loading: bool = True):
        """Set loading state for the table."""
        # Could add a loading overlay or spinner
        pass