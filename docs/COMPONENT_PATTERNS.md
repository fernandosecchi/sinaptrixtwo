# Component Patterns Documentation

## Overview

This application uses a component-based architecture for NiceGUI UI elements, providing reusable components that encapsulate common UI patterns and behaviors.

## Directory Structure

```
src/ui/
├── components/
│   ├── __init__.py         # Component exports
│   ├── data_table.py       # Reusable data table
│   ├── search_bar.py       # Search input with buttons
│   ├── crud_dialog.py      # CRUD operations dialog
│   ├── stats_card.py       # Statistics display cards
│   └── confirm_dialog.py   # Confirmation dialogs
└── pages/
    ├── leads_refactored.py # Example using components
    └── ...
```

## Available Components

### 1. DataTable

A reusable table component with sorting, pagination, and actions.

```python
from src.ui.components import DataTable, TableColumn

# Define columns
columns = [
    TableColumn('id', 'ID', 'id'),
    TableColumn('name', 'Name', 'name'),
    TableColumn('email', 'Email', 'email'),
]

# Create table
table = DataTable(
    title="Users List",
    columns=columns,
    on_view=lambda row: show_details(row),
    on_edit=lambda row: edit_item(row),
    on_delete=lambda row: delete_item(row),
    searchable_fields=['name', 'email']
)

# Load data
table.load_data(users_list)

# Filter data
table.filter_data("search term")
```

**Features:**
- Column configuration with sorting
- Built-in pagination
- Action buttons (view, edit, delete)
- Search/filter functionality
- Stats display

### 2. SearchBar

A search input component with search and clear buttons.

```python
from src.ui.components import SearchBar

search_bar = SearchBar(
    placeholder="Search users...",
    on_search=lambda value: load_data(value),
    on_clear=lambda: load_data(),
    search_button_text='Search',
    clear_button_text='Clear'
)

# Get current value
value = search_bar.get_value()

# Set value programmatically
search_bar.set_value("search term")

# Clear the search
search_bar.clear()
```

**Features:**
- Customizable placeholder text
- Search on Enter key
- Clear button
- Async callback support
- Disable/enable functionality

### 3. CrudDialog

A dialog component for Create, Read, Update, Delete operations.

```python
from src.ui.components import CrudDialog, FormField, DialogMode

# Define form fields
fields = [
    FormField('name', 'Name', required=True),
    FormField('email', 'Email', field_type='email', required=True),
    FormField('role', 'Role', field_type='select', options={
        'admin': 'Administrator',
        'user': 'User'
    }),
    FormField('notes', 'Notes', field_type='textarea'),
]

# Create dialog
dialog = CrudDialog(
    title="User Management",
    fields=fields,
    on_save=lambda data, mode: save_user(data, mode),
    on_delete=lambda data: delete_user(data['id'])
)

# Open for create
dialog.open(DialogMode.CREATE)

# Open for edit with existing data
dialog.open(DialogMode.EDIT, user_data)

# Open for view (read-only)
dialog.open(DialogMode.VIEW, user_data)
```

**Supported Field Types:**
- `text` - Regular text input
- `email` - Email input with validation
- `number` - Numeric input
- `select` - Dropdown selection
- `textarea` - Multi-line text
- `checkbox` - Boolean checkbox

**Field Options:**
- `required` - Makes field mandatory
- `placeholder` - Placeholder text
- `default_value` - Default for new records
- `readonly_in_edit` - Read-only in edit mode
- `full_width` - Takes full row width
- `validation_fn` - Custom validation function

### 4. StatsCard

Cards for displaying statistics and metrics.

```python
from src.ui.components import StatsCard, StatsGrid

# Individual card
card = StatsCard(
    title="Total Users",
    value=150,
    subtitle="Active users this month",
    icon="people",
    color="blue",
    trend_value=12.5,
    trend_direction="up",
    format_value="{:,}"  # Format with thousands separator
)

# Update value dynamically
card.update_value(200, animate=True)

# Grid of stats cards
grid = StatsGrid(columns=4)
grid.create_card(title="Sales", value=45000, format_value="${:,.0f}")
grid.create_card(title="Growth", value=23.5, format_value="{:.1f}%")
```

**Features:**
- Icon support
- Color themes (blue, green, red, orange, purple, gray)
- Trend indicators (up/down arrows)
- Value formatting
- Animation on update
- Clickable cards with callbacks

### 5. ConfirmDialog

Confirmation and alert dialogs.

```python
from src.ui.components import ConfirmDialog, AlertDialog

# Confirmation dialog
ConfirmDialog.ask(
    title="Delete Item",
    message="This action cannot be undone!",
    on_confirm=lambda: delete_item(id),
    on_cancel=lambda: print("Cancelled"),
    confirm_color="negative",
    icon="warning",
    icon_color="red"
)

# Alert dialog
AlertDialog.show(
    title="Success",
    message="Operation completed successfully!",
    type="success"  # info, success, warning, error
)

# Custom confirmation
dialog = ConfirmDialog(
    title="Custom Confirm",
    message="Are you sure?",
    confirm_text="Yes, proceed",
    cancel_text="No, go back",
    confirm_color="positive"
)
dialog.open()
```

**Dialog Types for Alerts:**
- `info` - Blue info icon
- `success` - Green checkmark
- `warning` - Orange warning icon
- `error` - Red error icon

## Component Patterns

### 1. Async Support

All components support both sync and async callbacks:

```python
# Async callback
async def async_search(term):
    results = await fetch_data(term)
    return results

search_bar = SearchBar(on_search=async_search)

# Sync callback
def sync_search(term):
    return filter_data(term)

search_bar = SearchBar(on_search=sync_search)
```

### 2. Event Handling

Components handle events internally and expose clean callbacks:

```python
# Component handles UI events internally
dialog = CrudDialog(
    on_save=lambda data, mode: {
        DialogMode.CREATE: create_item(data),
        DialogMode.EDIT: update_item(data)
    }[mode]
)
```

### 3. State Management

Components manage their own state:

```python
# Component maintains internal state
stats_card = StatsCard(title="Users", value=0)

# Update state through methods
stats_card.update_value(100)
stats_card.update_trend(5.2, "up")
```

### 4. Composition

Components can be composed together:

```python
# Compose multiple components
with ui.column():
    search_bar = SearchBar(on_search=filter_data)
    stats_grid = StatsGrid()
    table = DataTable(columns=columns)
    dialog = CrudDialog(fields=fields)
```

## Usage Example

Here's a complete example from the refactored leads page:

```python
from src.ui.components import (
    SearchBar, StatsGrid, CrudDialog,
    FormField, DialogMode, ConfirmDialog
)

# Search functionality
search_bar = SearchBar(
    placeholder="Search leads...",
    on_search=lambda term: load_leads(term),
    on_clear=lambda: load_leads()
)

# Statistics display
stats_grid = StatsGrid(columns=5)
stats_grid.create_card(title='Total', value=100, icon='groups')
stats_grid.create_card(title='Conversion Rate', value=23.5,
                       format_value='{:.1f}%', trend_value=5.2,
                       trend_direction='up')

# CRUD dialog
lead_dialog = CrudDialog(
    title="Lead",
    fields=[
        FormField('name', 'Name', required=True),
        FormField('email', 'Email', field_type='email', required=True),
        FormField('status', 'Status', field_type='select',
                  options={'lead': 'Lead', 'client': 'Client'})
    ],
    on_save=save_lead,
    on_delete=delete_lead
)

# Confirmation before delete
ConfirmDialog.ask(
    title="Delete Lead",
    message="Are you sure you want to delete this lead?",
    on_confirm=lambda: perform_delete(lead_id),
    confirm_color="negative"
)
```

## Best Practices

### 1. Component Initialization

Initialize components once and reuse them:

```python
# Good - Initialize once
class MyPage:
    def __init__(self):
        self.search_bar = SearchBar(on_search=self.search)
        self.dialog = CrudDialog(fields=self.fields)

    async def search(self, term):
        # Reuse the same component instance
        results = await self.fetch_results(term)
```

### 2. Callback Patterns

Use lambdas for simple callbacks, methods for complex logic:

```python
# Simple callback - use lambda
SearchBar(on_clear=lambda: table.load_data([]))

# Complex logic - use method
async def handle_save(data, mode):
    if mode == DialogMode.CREATE:
        validate_new_item(data)
        await create_item(data)
    else:
        await update_item(data)

CrudDialog(on_save=handle_save)
```

### 3. Error Handling

Components should handle errors gracefully:

```python
async def save_with_error_handling(data, mode):
    try:
        await save_to_database(data)
        ui.notify("Saved successfully", type="positive")
    except ValidationError as e:
        ui.notify(f"Validation error: {e}", type="warning")
    except Exception as e:
        ui.notify(f"Error: {e}", type="negative")

dialog = CrudDialog(on_save=save_with_error_handling)
```

### 4. Component Communication

Use callbacks to communicate between components:

```python
# Components communicate through callbacks
async def on_search(term):
    results = await search_database(term)
    table.load_data(results)
    stats_grid.update_card(0, len(results))

search_bar = SearchBar(on_search=on_search)
```

## Adding New Components

To add a new reusable component:

1. Create the component file in `src/ui/components/`
2. Define the component class with clear initialization parameters
3. Implement internal UI setup in `_setup_ui()` method
4. Provide public methods for interaction
5. Export in `src/ui/components/__init__.py`
6. Document usage in this file

Example structure:

```python
# src/ui/components/my_component.py
from nicegui import ui
from typing import Optional, Callable

class MyComponent:
    def __init__(self,
                 title: str = "",
                 on_action: Optional[Callable] = None):
        self.title = title
        self.on_action = on_action
        self._setup_ui()

    def _setup_ui(self):
        """Internal UI setup."""
        # Create UI elements
        pass

    def public_method(self):
        """Public method for interaction."""
        pass
```

## Testing Components

Components can be tested in isolation:

```python
# Create a test page
@ui.page("/test-components")
def test_page():
    with ui.column():
        # Test SearchBar
        search = SearchBar(
            on_search=lambda v: ui.notify(f"Searched: {v}")
        )

        # Test StatsCard
        stats = StatsCard(
            title="Test Card",
            value=100,
            color="green"
        )

        # Test CrudDialog
        dialog = CrudDialog(
            title="Test Dialog",
            fields=[FormField("test", "Test Field")]
        )
        ui.button("Open Dialog", on_click=lambda: dialog.open())
```

## Migration Guide

To migrate existing pages to use components:

1. Identify repeated UI patterns
2. Replace with appropriate components
3. Move business logic to callbacks
4. Test functionality

Before:
```python
# Manual search implementation
search_input = ui.input('Search...')
ui.button('Search', on_click=lambda: search(search_input.value))
ui.button('Clear', on_click=lambda: clear_search())
```

After:
```python
# Using SearchBar component
search_bar = SearchBar(
    placeholder="Search...",
    on_search=search,
    on_clear=clear_search
)
```

## Troubleshooting

### Component not updating

Ensure you're calling update methods:
```python
# Update component state
stats_card.update_value(new_value)
table.refresh()
```

### Async callbacks not working

Check if the component supports async:
```python
# Component detects and handles async automatically
import asyncio

if asyncio.iscoroutinefunction(callback):
    await callback()
else:
    callback()
```

### Dialog not opening

Make sure dialog is initialized before opening:
```python
# Initialize first
dialog = CrudDialog(...)

# Then open
dialog.open(DialogMode.CREATE)
```

## Conclusion

The component-based architecture provides:
- **Reusability**: Write once, use everywhere
- **Consistency**: Uniform UI/UX across the application
- **Maintainability**: Centralized component logic
- **Testability**: Components can be tested in isolation
- **Flexibility**: Customizable through parameters and callbacks

For questions or to add new components, refer to existing components as examples and follow the established patterns.