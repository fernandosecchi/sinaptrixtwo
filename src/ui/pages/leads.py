"""Leads management page with reusable components."""
from datetime import datetime
from typing import Dict, List
from nicegui import ui
from sqlalchemy import select, update
from src.database import AsyncSessionLocal
from src.models.leads.lead import Lead
from src.models.enums import LeadStatus, LeadSource
from src.ui.layouts import theme_layout
from src.ui.components import (
    SearchBar,
    CrudDialog,
    FormField,
    DialogMode,
    ConfirmDialog
)


def create_leads_page():
    """Register the leads management page with reusable components."""

    @ui.page("/leads")
    async def leads_page():
        breadcrumb_items = [
            ('Gestión', '/'),
            ('Leads', '/leads')
        ]
        with theme_layout('Leads', breadcrumb_items=breadcrumb_items):
            with ui.column().classes('w-full gap-2'):
                # Compact header with add button
                with ui.row().classes('w-full items-center justify-between mb-2'):
                    # Remove redundant title since it's in breadcrumbs
                    ui.button('Nuevo', on_click=lambda: lead_dialog.open(DialogMode.CREATE), icon='add').props('size=sm color=primary')

                # Search bar component
                async def search_leads(search_term: str):
                    await load_leads(search_term, update_stats=False)

                async def clear_search():
                    await load_leads(None, update_stats=False)

                search_bar = SearchBar(
                    placeholder="Buscar...",
                    on_search=search_leads,
                    on_clear=clear_search,
                    search_button_text='',  # Icon only
                    clear_button_text=''     # Icon only
                )

                # Minimal stats row with refresh
                with ui.row().classes('w-full items-center justify-between mb-2'):
                    stats_container = ui.row().classes('gap-2 items-center')
                    # Refresh button (will be at the right)
                    ui.button(icon='refresh', on_click=lambda: load_leads()).props('size=sm flat dense color=gray')

                # Kanban board container
                kanban_container = ui.row().classes('w-full gap-4 overflow-x-auto')

                # Source options for lead form
                source_options = {
                    LeadSource.WEBSITE.value: 'Sitio Web',
                    LeadSource.REFERRAL.value: 'Referido',
                    LeadSource.SOCIAL_MEDIA.value: 'Redes Sociales',
                    LeadSource.EMAIL.value: 'Email',
                    LeadSource.PHONE.value: 'Teléfono',
                    LeadSource.EVENT.value: 'Evento',
                    LeadSource.OTHER.value: 'Otro'
                }

                # Define save_lead function before using it
                async def save_lead(data: dict, mode: DialogMode):
                    """Save lead using the dialog data."""
                    try:
                        async with AsyncSessionLocal() as session:
                            if mode == DialogMode.CREATE:
                                new_lead = Lead(
                                    first_name=data['first_name'],
                                    last_name=data['last_name'],
                                    email=data['email'],
                                    phone=data.get('phone'),
                                    company=data.get('company'),
                                    position=data.get('position'),
                                    source=data.get('source'),
                                    notes=data.get('notes'),
                                    status=LeadStatus.LEAD.value
                                )
                                session.add(new_lead)
                                message = f'Lead {data["first_name"]} {data["last_name"]} creado exitosamente'
                            else:  # EDIT mode
                                stmt = (
                                    update(Lead)
                                    .where(Lead.id == data['id'])
                                    .values(
                                        first_name=data['first_name'],
                                        last_name=data['last_name'],
                                        email=data['email'],
                                        phone=data.get('phone'),
                                        company=data.get('company'),
                                        position=data.get('position'),
                                        source=data.get('source'),
                                        notes=data.get('notes'),
                                        updated_at=datetime.utcnow()
                                    )
                                )
                                await session.execute(stmt)
                                message = f'Lead actualizado exitosamente'

                            await session.commit()

                        ui.notify(message, type='positive')
                        await load_leads()
                    except Exception as e:
                        ui.notify(f'Error: {e}', type='negative')

                async def delete_lead(data: dict):
                    """Delete a lead."""
                    try:
                        async with AsyncSessionLocal() as session:
                            lead = await session.get(Lead, data['id'])
                            if lead:
                                await session.delete(lead)
                                await session.commit()
                                ui.notify('Lead eliminado exitosamente', type='info')
                                await load_leads()
                    except Exception as e:
                        ui.notify(f'Error: {e}', type='negative')

                # Now create the lead dialog after defining the functions
                lead_dialog = CrudDialog(
                    title="Lead",
                    fields=[
                        FormField('first_name', 'Nombre', required=True, full_width=False),
                        FormField('last_name', 'Apellido', required=True, full_width=False),
                        FormField('email', 'Email', field_type='email', required=True),
                        FormField('phone', 'Teléfono', full_width=False),
                        FormField('position', 'Cargo', full_width=False),
                        FormField('company', 'Empresa'),
                        FormField('source', 'Origen', field_type='select', options=source_options, default_value=LeadSource.WEBSITE.value),
                        FormField('notes', 'Notas', field_type='textarea')
                    ],
                    on_save=save_lead,
                    on_delete=delete_lead,
                    width='w-[500px]'
                )

                async def load_stats():
                    """Load and display minimal statistics."""
                    try:
                        async with AsyncSessionLocal() as session:
                            result = await session.execute(select(Lead))
                            all_leads = result.scalars().all()

                            # Calculate stats
                            total = len(all_leads)
                            leads_count = sum(1 for l in all_leads if l.status == LeadStatus.LEAD.value)
                            prospects_count = sum(1 for l in all_leads if l.status == LeadStatus.PROSPECT.value)
                            clients_count = sum(1 for l in all_leads if l.status == LeadStatus.CLIENT.value)
                            rate = (clients_count / total * 100) if total > 0 else 0

                            # Clear and recreate minimal stats
                            stats_container.clear()

                            with stats_container:
                                # Ultra compact stats - just numbers with tooltips
                                ui.label(f'{total}').classes('text-xs text-gray-600').tooltip('Total')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{leads_count}').classes('text-xs text-blue-600').tooltip('Leads')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{prospects_count}').classes('text-xs text-orange-600').tooltip('Prospects')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{clients_count}').classes('text-xs text-green-600').tooltip('Clientes')
                                ui.label('•').classes('text-gray-400')
                                ui.label(f'{rate:.0f}%').classes('text-xs text-purple-600').tooltip('Conversión')

                    except Exception as e:
                        ui.notify(f'Error al cargar estadísticas: {e}', type='negative')

                async def load_leads(search_term: str = None, update_stats: bool = True):
                    """Load and display leads in Kanban view."""
                    kanban_container.clear()

                    # Only update stats on initial load or explicit request
                    if update_stats:
                        await load_stats()

                    try:
                        async with AsyncSessionLocal() as session:
                            # Create query with search filter
                            query = select(Lead).order_by(Lead.created_at.desc())

                            # Apply search filter if present
                            if search_term:
                                search_pattern = f"%{search_term}%"
                                query = query.where(
                                    (Lead.first_name.ilike(search_pattern)) |
                                    (Lead.last_name.ilike(search_pattern)) |
                                    (Lead.email.ilike(search_pattern)) |
                                    (Lead.company.ilike(search_pattern))
                                )

                            result = await session.execute(query)
                            leads = result.scalars().all()

                        # Group leads by status
                        leads_by_status: Dict[str, List[Lead]] = {
                            LeadStatus.LEAD.value: [],
                            LeadStatus.PROSPECT.value: [],
                            LeadStatus.CLIENT.value: [],
                        }

                        for lead in leads:
                            if lead.status != LeadStatus.LOST.value:
                                leads_by_status[lead.status].append(lead)

                        # Status configurations
                        status_config = {
                            LeadStatus.LEAD.value: {
                                'title': 'Leads',
                                'color': 'bg-blue-100',
                                'icon': 'person_add',
                                'next_status': LeadStatus.PROSPECT.value,
                                'next_action': 'Convertir a Prospect'
                            },
                            LeadStatus.PROSPECT.value: {
                                'title': 'Prospects',
                                'color': 'bg-orange-100',
                                'icon': 'people',
                                'next_status': LeadStatus.CLIENT.value,
                                'next_action': 'Convertir a Cliente'
                            },
                            LeadStatus.CLIENT.value: {
                                'title': 'Clientes',
                                'color': 'bg-green-100',
                                'icon': 'verified_user',
                                'next_status': None,
                                'next_action': None
                            }
                        }

                        # Create Kanban columns
                        with kanban_container:
                            for status, config in status_config.items():
                                with ui.column().classes('flex-1 min-w-80'):
                                    # Column header
                                    with ui.card().classes(f'w-full p-4 {config["color"]}'):
                                        with ui.row().classes('items-center gap-2'):
                                            ui.icon(config['icon'])
                                            ui.label(config['title']).classes('font-bold text-lg')
                                            ui.label(f'({len(leads_by_status[status])})').classes('text-gray-600')

                                    # Lead cards
                                    column_container = ui.column().classes('w-full gap-2')

                                    if not leads_by_status[status]:
                                        with column_container:
                                            ui.label('Sin registros').classes('text-gray-400 italic p-4')

                                    for lead in leads_by_status[status]:
                                        with column_container:
                                            with ui.card().classes('w-full p-4 hover:shadow-lg transition-shadow cursor-pointer'):
                                                # Lead info
                                                ui.label(f'{lead.first_name} {lead.last_name}').classes('font-bold text-lg')

                                                if lead.company:
                                                    with ui.row().classes('items-center gap-1'):
                                                        ui.icon('business', size='sm').classes('text-gray-500')
                                                        ui.label(lead.company).classes('text-sm text-gray-600')

                                                with ui.row().classes('items-center gap-1'):
                                                    ui.icon('email', size='sm').classes('text-gray-500')
                                                    ui.label(lead.email).classes('text-sm text-gray-600')

                                                if lead.phone:
                                                    with ui.row().classes('items-center gap-1'):
                                                        ui.icon('phone', size='sm').classes('text-gray-500')
                                                        ui.label(lead.phone).classes('text-sm text-gray-600')

                                                if lead.source:
                                                    source_label = source_options.get(lead.source, lead.source)
                                                    ui.label(f'Origen: {source_label}').classes('text-xs text-gray-500 mt-2')

                                                # Timestamps
                                                ui.label(f'Creado: {lead.created_at.strftime("%d/%m/%Y")}').classes('text-xs text-gray-400 mt-1')

                                                # Action buttons
                                                with ui.row().classes('w-full gap-2 mt-3'):
                                                    # Edit button
                                                    def edit_lead(lead_data=lead):
                                                        lead_dict = {
                                                            'id': lead_data.id,
                                                            'first_name': lead_data.first_name,
                                                            'last_name': lead_data.last_name,
                                                            'email': lead_data.email,
                                                            'phone': lead_data.phone,
                                                            'company': lead_data.company,
                                                            'position': lead_data.position,
                                                            'source': lead_data.source,
                                                            'notes': lead_data.notes
                                                        }
                                                        lead_dialog.open(DialogMode.EDIT, lead_dict)

                                                    ui.button(
                                                        icon='edit',
                                                        on_click=edit_lead
                                                    ).props('size=sm flat round dense')

                                                    if config['next_action']:
                                                        async def convert_lead(lead_id=lead.id, next_status=config['next_status']):
                                                            ConfirmDialog.ask(
                                                                title='Confirmar Conversión',
                                                                message=f'¿Deseas {config["next_action"].lower()}?',
                                                                on_confirm=lambda: do_convert(lead_id, next_status),
                                                                confirm_text='Sí, convertir',
                                                                confirm_color='positive'
                                                            )

                                                        async def do_convert(lead_id, next_status):
                                                            try:
                                                                async with AsyncSessionLocal() as session:
                                                                    stmt = (
                                                                        update(Lead)
                                                                        .where(Lead.id == lead_id)
                                                                        .values(
                                                                            status=next_status,
                                                                            updated_at=datetime.utcnow()
                                                                        )
                                                                    )

                                                                    if next_status == LeadStatus.PROSPECT.value:
                                                                        stmt = stmt.values(converted_to_prospect_at=datetime.utcnow())
                                                                    elif next_status == LeadStatus.CLIENT.value:
                                                                        stmt = stmt.values(converted_to_client_at=datetime.utcnow())

                                                                    await session.execute(stmt)
                                                                    await session.commit()

                                                                ui.notify('Lead convertido exitosamente', type='positive')
                                                                await load_leads()
                                                            except Exception as e:
                                                                ui.notify(f'Error: {e}', type='negative')

                                                        ui.button(
                                                            config['next_action'],
                                                            on_click=convert_lead
                                                        ).props('size=sm color=primary dense').classes('flex-1')

                                                    if status != LeadStatus.CLIENT.value:
                                                        async def mark_as_lost(lead_id=lead.id):
                                                            ConfirmDialog.ask(
                                                                title='Marcar como Perdido',
                                                                message='¿Estás seguro de marcar este lead como perdido?',
                                                                on_confirm=lambda: do_mark_lost(lead_id),
                                                                confirm_color='negative',
                                                                icon='warning',
                                                                icon_color='red'
                                                            )

                                                        async def do_mark_lost(lead_id):
                                                            try:
                                                                async with AsyncSessionLocal() as session:
                                                                    stmt = (
                                                                        update(Lead)
                                                                        .where(Lead.id == lead_id)
                                                                        .values(
                                                                            status=LeadStatus.LOST.value,
                                                                            updated_at=datetime.utcnow()
                                                                        )
                                                                    )
                                                                    await session.execute(stmt)
                                                                    await session.commit()

                                                                ui.notify('Lead marcado como perdido', type='info')
                                                                await load_leads()
                                                            except Exception as e:
                                                                ui.notify(f'Error: {e}', type='negative')

                                                        ui.button(
                                                            'Perdido',
                                                            on_click=mark_as_lost
                                                        ).props('size=sm color=negative dense flat')

                    except Exception as e:
                        with kanban_container:
                            ui.label(f'Error al cargar leads: {e}').classes('text-red-500')

                # Load initial data
                await load_leads()