"""Lead service for business logic operations."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.leads.lead_repository import LeadRepository
from src.models.leads.lead import Lead
from src.models.enums import LeadStatus, LeadSource
from src.schemas.leads.lead import LeadCreate, LeadUpdate, LeadStatistics


class LeadService:
    """Service layer for lead operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize lead service with database session."""
        self.repository = LeadRepository(session)
    
    async def create_lead(self, lead_data: LeadCreate) -> Lead:
        """Create a new lead with validation."""
        # Check if email already exists
        existing_lead = await self.repository.get_by_email(lead_data.email)
        if existing_lead:
            raise ValueError(f"Ya existe un lead con el email {lead_data.email}")
        
        # Create lead
        return await self.repository.create(
            first_name=lead_data.first_name,
            last_name=lead_data.last_name,
            email=lead_data.email,
            phone=lead_data.phone,
            company=lead_data.company,
            position=lead_data.position,
            notes=lead_data.notes,
            source=lead_data.source.value if lead_data.source else None,
            status=LeadStatus.LEAD.value
        )
    
    async def get_lead(self, lead_id: int) -> Optional[Lead]:
        """Get lead by ID."""
        return await self.repository.get(lead_id)
    
    async def get_all_leads(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Lead]:
        """Get all leads with optional filtering."""
        if status:
            return await self.repository.get_by_status(status)
        return await self.repository.get_all(
            skip=skip,
            limit=limit,
            order_by=Lead.created_at.desc()
        )
    
    async def update_lead(
        self,
        lead_id: int,
        lead_data: LeadUpdate
    ) -> Optional[Lead]:
        """Update lead information."""
        # Check if email is being changed and if it's already taken
        if lead_data.email:
            existing_lead = await self.repository.get_by_email(lead_data.email)
            if existing_lead and existing_lead.id != lead_id:
                raise ValueError(f"El email {lead_data.email} ya está registrado")
        
        # Build update data (exclude None values)
        update_data = {
            k: v for k, v in lead_data.model_dump().items() 
            if v is not None
        }
        
        if not update_data:
            return await self.get_lead(lead_id)
        
        # Convert enum to string if needed
        if 'source' in update_data:
            update_data['source'] = update_data['source'].value
        
        update_data['updated_at'] = datetime.utcnow()
        
        return await self.repository.update(lead_id, **update_data)
    
    async def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead."""
        return await self.repository.delete(lead_id)
    
    async def convert_to_prospect(self, lead_id: int) -> bool:
        """Convert a lead to prospect status."""
        lead = await self.repository.get(lead_id)
        if not lead:
            raise ValueError(f"Lead con ID {lead_id} no encontrado")
        
        if lead.status != LeadStatus.LEAD.value:
            raise ValueError(f"Solo se pueden convertir leads a prospects")
        
        return await self.repository.convert_to_prospect(lead_id)
    
    async def convert_to_client(self, lead_id: int) -> bool:
        """Convert a prospect to client status."""
        lead = await self.repository.get(lead_id)
        if not lead:
            raise ValueError(f"Lead con ID {lead_id} no encontrado")
        
        if lead.status == LeadStatus.CLIENT.value:
            raise ValueError(f"El lead ya es un cliente")
        
        if lead.status == LeadStatus.LOST.value:
            raise ValueError(f"No se puede convertir un lead perdido")
        
        # If it's a lead, first convert to prospect
        if lead.status == LeadStatus.LEAD.value:
            await self.repository.convert_to_prospect(lead_id)
        
        return await self.repository.convert_to_client(lead_id)
    
    async def mark_as_lost(self, lead_id: int) -> bool:
        """Mark a lead as lost."""
        lead = await self.repository.get(lead_id)
        if not lead:
            raise ValueError(f"Lead con ID {lead_id} no encontrado")
        
        if lead.status == LeadStatus.CLIENT.value:
            raise ValueError(f"No se puede marcar un cliente como perdido")
        
        return await self.repository.mark_as_lost(lead_id)
    
    async def get_leads_by_status(self, status: LeadStatus) -> List[Lead]:
        """Get all leads with specific status."""
        return await self.repository.get_by_status(status.value)
    
    async def get_statistics(self) -> LeadStatistics:
        """Get lead statistics."""
        stats = await self.repository.get_statistics()
        
        return LeadStatistics(
            total=stats['total'],
            leads=stats.get(LeadStatus.LEAD.value, 0),
            prospects=stats.get(LeadStatus.PROSPECT.value, 0),
            clients=stats.get(LeadStatus.CLIENT.value, 0),
            lost=stats.get(LeadStatus.LOST.value, 0),
            conversion_rate=stats['conversion_rate']
        )
    
    async def search_leads(self, search_term: str) -> List[Lead]:
        """Search leads by name, email, or company."""
        if not search_term:
            return await self.get_all_leads()
        return await self.repository.search(search_term)
    
    async def get_leads_count(self) -> int:
        """Get total count of leads."""
        return await self.repository.count()
    
    async def validate_status_transition(
        self,
        current_status: LeadStatus,
        new_status: LeadStatus
    ) -> bool:
        """Validate if status transition is allowed."""
        # Define allowed transitions
        allowed_transitions = {
            LeadStatus.LEAD: [LeadStatus.PROSPECT, LeadStatus.LOST],
            LeadStatus.PROSPECT: [LeadStatus.CLIENT, LeadStatus.LOST],
            LeadStatus.CLIENT: [],  # Clients cannot change status
            LeadStatus.LOST: []  # Lost leads cannot change status
        }
        
        return new_status in allowed_transitions.get(current_status, [])