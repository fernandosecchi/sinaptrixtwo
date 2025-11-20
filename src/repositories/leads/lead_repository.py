"""Lead repository for lead-specific database operations."""
from typing import List, Dict
from datetime import datetime
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.leads.lead import Lead
from src.models.enums import LeadStatus
from src.repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    """Repository for Lead model operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize lead repository."""
        super().__init__(Lead, session)
    
    async def get_by_status(self, status: str) -> List[Lead]:
        """Get all leads with a specific status."""
        query = select(Lead).where(Lead.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_email(self, email: str) -> Lead:
        """Get lead by email address."""
        query = select(Lead).where(Lead.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def convert_to_prospect(self, lead_id: int) -> bool:
        """Convert a lead to prospect status."""
        stmt = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(
                status=LeadStatus.PROSPECT.value,
                converted_to_prospect_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def convert_to_client(self, lead_id: int) -> bool:
        """Convert a lead/prospect to client status."""
        stmt = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(
                status=LeadStatus.CLIENT.value,
                converted_to_client_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def mark_as_lost(self, lead_id: int) -> bool:
        """Mark a lead as lost."""
        stmt = (
            update(Lead)
            .where(Lead.id == lead_id)
            .values(
                status=LeadStatus.LOST.value,
                updated_at=datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_statistics(self) -> Dict[str, int]:
        """Get lead statistics by status."""
        query = select(
            Lead.status,
            func.count(Lead.id)
        ).group_by(Lead.status)
        
        result = await self.session.execute(query)
        stats = {row[0]: row[1] for row in result}
        
        # Ensure all statuses are present
        for status in LeadStatus:
            if status.value not in stats:
                stats[status.value] = 0
        
        # Calculate conversion rate
        total = sum(stats.values())
        stats['total'] = total
        stats['conversion_rate'] = (
            (stats[LeadStatus.CLIENT.value] / total * 100) if total > 0 else 0
        )
        
        return stats
    
    async def search(self, term: str) -> List[Lead]:
        """Search leads by name, email, or company."""
        search_term = f"%{term}%"
        query = select(Lead).where(
            (Lead.first_name.ilike(search_term)) |
            (Lead.last_name.ilike(search_term)) |
            (Lead.email.ilike(search_term)) |
            (Lead.company.ilike(search_term))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())