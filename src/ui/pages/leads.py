"""Leads management page with pipeline view."""
from datetime import datetime
from typing import Dict, List
from nicegui import ui
from sqlalchemy import select, update
from src.database import AsyncSessionLocal
from src.models.lead import Lead
from src.models.enums import LeadStatus, LeadSource
from src.ui.layouts import theme_layout


def create_leads_page():
    """Register the leads management page."""
    
    @ui.page("/leads")
    async def leads_page():
        with theme_layout('Gestión de Leads'):
            with ui.column().classes('w-full gap-4'):
                # Header with title and add button
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label('Pipeline de Ventas').classes('text-3xl font-bold text-primary')
                    ui.button('Nuevo Lead', on_click=lambda: lead_dialog.open(), icon='add').props('color=primary')
                
                # Stats cards
                with ui.row().classes('w-full gap-4'):
                    stats_container = ui.row().classes('w-full gap-4')
                
                # Kanban board container
                kanban_container = ui.row().classes('w-full gap-4 overflow-x-auto')
                
                # Lead dialog for add/edit
                with ui.dialog() as lead_dialog, ui.card().classes('w-96'):
                    ui.label('Agregar Lead').classes('text-xl font-semibold')
                    
                    # Form inputs
                    with ui.row().classes('w-full gap-2'):
                        first_name_input = ui.input('Nombre*').props('outlined dense').classes('flex-1')
                        last_name_input = ui.input('Apellido*').props('outlined dense').classes('flex-1')
                    
                    email_input = ui.input('Email*').props('outlined dense').classes('w-full')
                    
                    with ui.row().classes('w-full gap-2'):
                        phone_input = ui.input('Teléfono').props('outlined dense').classes('flex-1')
                        position_input = ui.input('Cargo').props('outlined dense').classes('flex-1')
                    
                    company_input = ui.input('Empresa').props('outlined dense').classes('w-full')
                    
                    # Source dropdown
                    source_options = {
                        LeadSource.WEBSITE.value: 'Sitio Web',
                        LeadSource.REFERRAL.value: 'Referido',
                        LeadSource.SOCIAL_MEDIA.value: 'Redes Sociales',
                        LeadSource.EMAIL.value: 'Email',
                        LeadSource.PHONE.value: 'Teléfono',
                        LeadSource.EVENT.value: 'Evento',
                        LeadSource.OTHER.value: 'Otro'
                    }
                    source_select = ui.select(
                        source_options,
                        label='Origen',
                        value=LeadSource.WEBSITE.value
                    ).props('outlined dense').classes('w-full')
                    
                    notes_input = ui.textarea('Notas').props('outlined dense').classes('w-full')
                    
                    # Dialog actions
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('Cancelar', on_click=lead_dialog.close).props('flat')
                        
                        async def save_lead():
                            if not first_name_input.value or not last_name_input.value or not email_input.value:
                                ui.notify('Nombre, Apellido y Email son requeridos', type='warning')
                                return
                            
                            try:
                                async with AsyncSessionLocal() as session:
                                    new_lead = Lead(
                                        first_name=first_name_input.value,
                                        last_name=last_name_input.value,
                                        email=email_input.value,
                                        phone=phone_input.value or None,
                                        company=company_input.value or None,
                                        position=position_input.value or None,
                                        source=source_select.value if source_select.value else None,
                                        notes=notes_input.value or None,
                                        status=LeadStatus.LEAD.value
                                    )
                                    session.add(new_lead)
                                    await session.commit()
                                
                                ui.notify(f'Lead {first_name_input.value} {last_name_input.value} creado exitosamente', type='positive')
                                
                                # Clear form
                                first_name_input.value = ''
                                last_name_input.value = ''
                                email_input.value = ''
                                phone_input.value = ''
                                company_input.value = ''
                                position_input.value = ''
                                notes_input.value = ''
                                source_select.value = LeadSource.WEBSITE.value
                                
                                lead_dialog.close()
                                await load_leads()
                            except Exception as e:
                                ui.notify(f'Error al crear lead: {e}', type='negative')
                        
                        ui.button('Guardar', on_click=save_lead).props('color=primary')
                
                async def load_stats():
                    """Load and display statistics."""
                    stats_container.clear()
                    
                    try:
                        async with AsyncSessionLocal() as session:
                            result = await session.execute(select(Lead))
                            all_leads = result.scalars().all()
                            
                            # Calculate stats
                            total = len(all_leads)
                            leads_count = sum(1 for l in all_leads if l.status == LeadStatus.LEAD.value)
                            prospects_count = sum(1 for l in all_leads if l.status == LeadStatus.PROSPECT.value)
                            clients_count = sum(1 for l in all_leads if l.status == LeadStatus.CLIENT.value)
                            
                            with stats_container:
                                # Total card
                                with ui.card().classes('flex-1 p-4'):
                                    ui.label('Total').classes('text-sm text-gray-600')
                                    ui.label(str(total)).classes('text-2xl font-bold')
                                
                                # Leads card
                                with ui.card().classes('flex-1 p-4'):
                                    ui.label('Leads').classes('text-sm text-gray-600')
                                    ui.label(str(leads_count)).classes('text-2xl font-bold text-blue-600')
                                
                                # Prospects card
                                with ui.card().classes('flex-1 p-4'):
                                    ui.label('Prospects').classes('text-sm text-gray-600')
                                    ui.label(str(prospects_count)).classes('text-2xl font-bold text-orange-600')
                                
                                # Clients card
                                with ui.card().classes('flex-1 p-4'):
                                    ui.label('Clientes').classes('text-sm text-gray-600')
                                    ui.label(str(clients_count)).classes('text-2xl font-bold text-green-600')
                                
                                # Conversion rate card
                                with ui.card().classes('flex-1 p-4'):
                                    ui.label('Tasa de Conversión').classes('text-sm text-gray-600')
                                    rate = (clients_count / total * 100) if total > 0 else 0
                                    ui.label(f'{rate:.1f}%').classes('text-2xl font-bold text-purple-600')
                    
                    except Exception as e:
                        with stats_container:
                            ui.label(f'Error al cargar estadísticas: {e}').classes('text-red-500')
                
                async def load_leads():
                    """Load and display leads in Kanban view."""
                    kanban_container.clear()
                    await load_stats()
                    
                    try:
                        async with AsyncSessionLocal() as session:
                            result = await session.execute(select(Lead).order_by(Lead.created_at.desc()))
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
                                                    if config['next_action']:
                                                        async def convert_lead(lead_id=lead.id, next_status=config['next_status']):
                                                            try:
                                                                async with AsyncSessionLocal() as session:
                                                                    # Update status
                                                                    stmt = (
                                                                        update(Lead)
                                                                        .where(Lead.id == lead_id)
                                                                        .values(
                                                                            status=next_status,
                                                                            updated_at=datetime.utcnow()
                                                                        )
                                                                    )
                                                                    
                                                                    # Update conversion timestamp
                                                                    if next_status == LeadStatus.PROSPECT.value:
                                                                        stmt = stmt.values(converted_to_prospect_at=datetime.utcnow())
                                                                    elif next_status == LeadStatus.CLIENT.value:
                                                                        stmt = stmt.values(converted_to_client_at=datetime.utcnow())
                                                                    
                                                                    await session.execute(stmt)
                                                                    await session.commit()
                                                                
                                                                ui.notify(f'Lead convertido exitosamente', type='positive')
                                                                await load_leads()
                                                            except Exception as e:
                                                                ui.notify(f'Error al convertir: {e}', type='negative')
                                                        
                                                        ui.button(
                                                            config['next_action'],
                                                            on_click=convert_lead
                                                        ).props('size=sm color=primary dense').classes('flex-1')
                                                    
                                                    async def mark_as_lost(lead_id=lead.id):
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
                                                    
                                                    if status != LeadStatus.CLIENT.value:
                                                        ui.button(
                                                            'Perdido',
                                                            on_click=mark_as_lost
                                                        ).props('size=sm color=negative dense flat')
                    
                    except Exception as e:
                        with kanban_container:
                            ui.label(f'Error al cargar leads: {e}').classes('text-red-500')
                
                # Load initial data
                await load_leads()
                
                # Refresh button
                with ui.row().classes('w-full justify-end mt-4'):
                    ui.button('Actualizar', on_click=load_leads, icon='refresh').props('flat color=primary')