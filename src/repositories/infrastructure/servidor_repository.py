"""Repository for Servidor iSeries management."""
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.infrastructure.servidor import Servidor, ProcessorTier, EstadoRegistro


class ServidorRepository(BaseRepository[Servidor]):
    """Repository for managing Servidor iSeries entities."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository."""
        super().__init__(Servidor, session)

    async def get_by_serial_number(self, numero_serie: str) -> Optional[Servidor]:
        """Get a servidor by serial number."""
        result = await self.session.execute(
            select(self.model).where(self.model.numero_serie == numero_serie)
        )
        return result.scalars().first()

    async def get_active_servers(self) -> List[Servidor]:
        """Get all active servers."""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.activo == True)
            .order_by(self.model.nombre_servidor)
        )
        return list(result.scalars().all())

    async def get_by_processor_tier(self, tier: ProcessorTier) -> List[Servidor]:
        """Get servers by processor tier."""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.processor_tier == tier)
            .order_by(self.model.nombre_servidor)
        )
        return list(result.scalars().all())

    async def get_by_estado(self, estado: EstadoRegistro) -> List[Servidor]:
        """Get servers by registration status."""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.estado_registro == estado)
            .order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())

    async def search_servers(
        self,
        query: Optional[str] = None,
        modelo: Optional[str] = None,
        processor_tier: Optional[ProcessorTier] = None,
        estado: Optional[EstadoRegistro] = None,
        activo: Optional[bool] = None,
        es_virtualizado: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Servidor]:
        """
        Search servers with multiple filters.

        Args:
            query: Text search in name, description, model, serial number
            modelo: Filter by model
            processor_tier: Filter by processor tier
            estado: Filter by registration status
            activo: Filter by active status
            es_virtualizado: Filter by virtualization status
            skip: Number of records to skip
            limit: Maximum number of records to return
        """
        stmt = select(self.model)

        # Apply filters
        filters = []

        if query:
            search_filter = or_(
                self.model.nombre_servidor.ilike(f"%{query}%"),
                self.model.descripcion.ilike(f"%{query}%"),
                self.model.modelo.ilike(f"%{query}%"),
                self.model.numero_serie.ilike(f"%{query}%"),
                self.model.ip_principal.ilike(f"%{query}%")
            )
            filters.append(search_filter)

        if modelo:
            filters.append(self.model.modelo.ilike(f"%{modelo}%"))

        if processor_tier:
            filters.append(self.model.processor_tier == processor_tier)

        if estado:
            filters.append(self.model.estado_registro == estado)

        if activo is not None:
            filters.append(self.model.activo == activo)

        if es_virtualizado is not None:
            filters.append(self.model.es_virtualizado == es_virtualizado)

        if filters:
            stmt = stmt.where(and_(*filters))

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        stmt = stmt.order_by(self.model.nombre_servidor)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about servers."""
        # Total servers
        total_stmt = select(func.count()).select_from(self.model)
        total_result = await self.session.execute(total_stmt)
        total_servers = total_result.scalar() or 0

        # Active servers
        active_stmt = select(func.count()).select_from(self.model).where(
            self.model.activo == True
        )
        active_result = await self.session.execute(active_stmt)
        active_servers = active_result.scalar() or 0

        # Virtualized servers
        virtual_stmt = select(func.count()).select_from(self.model).where(
            self.model.es_virtualizado == True
        )
        virtual_result = await self.session.execute(virtual_stmt)
        virtualized_servers = virtual_result.scalar() or 0

        # By processor tier
        tier_stmt = select(
            self.model.processor_tier,
            func.count().label('count')
        ).group_by(self.model.processor_tier)
        tier_result = await self.session.execute(tier_stmt)
        servers_by_tier = {row.processor_tier.value: row.count for row in tier_result}

        # By status
        status_stmt = select(
            self.model.estado_registro,
            func.count().label('count')
        ).group_by(self.model.estado_registro)
        status_result = await self.session.execute(status_stmt)
        servers_by_status = {row.estado_registro.value: row.count for row in status_result}

        return {
            'total_servers': total_servers,
            'active_servers': active_servers,
            'virtualized_servers': virtualized_servers,
            'physical_servers': total_servers - virtualized_servers,
            'servers_by_tier': servers_by_tier,
            'servers_by_status': servers_by_status
        }

    async def check_duplicate_serial(self, numero_serie: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a serial number already exists (excluding a specific ID)."""
        stmt = select(self.model).where(self.model.numero_serie == numero_serie)

        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)

        result = await self.session.execute(stmt)
        return result.scalars().first() is not None