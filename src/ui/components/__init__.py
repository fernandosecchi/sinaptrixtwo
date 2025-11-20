"""UI Components for NiceGUI application."""

from src.ui.components.data_table import DataTable, TableColumn
from src.ui.components.search_bar import SearchBar
from src.ui.components.crud_dialog import CrudDialog, FormField, DialogMode
from src.ui.components.stats_card import StatsCard, StatsGrid
from src.ui.components.confirm_dialog import ConfirmDialog, AlertDialog
from src.ui.components.header import AppHeader
from src.ui.components.navigation_drawer import NavigationDrawer, NavItem
from src.ui.components.footer import AppFooter, SimpleFooter

__all__ = [
    'DataTable',
    'TableColumn',
    'SearchBar',
    'CrudDialog',
    'FormField',
    'DialogMode',
    'StatsCard',
    'StatsGrid',
    'ConfirmDialog',
    'AlertDialog',
    'AppHeader',
    'NavigationDrawer',
    'NavItem',
    'AppFooter',
    'SimpleFooter'
]