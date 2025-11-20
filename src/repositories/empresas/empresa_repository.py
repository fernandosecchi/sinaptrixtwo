"""Empresa repository for data access."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.empresas.empresa import Empresa
from src.repositories.base import BaseRepository


class EmpresaRepository(BaseRepository[Empresa]):
    """Repository for Empresa model."""

    def __init__(self, session: AsyncSession):
        """Initialize empresa repository."""
        super().__init__(Empresa, session)

    async def get_active_empresas(
        self,
        include_relationships: bool = False
    ) -> List[Empresa]:
        """
        Get all active empresas.

        Args:
            include_relationships: Whether to include related data

        Returns:
            List of active empresas
        """
        query = select(self.model).where(
            self.model.is_active == True
        ).order_by(self.model.nombre)

        if include_relationships:
            query = query.options(
                selectinload(self.model.country),
                selectinload(self.model.state),
                selectinload(self.model.city),
                selectinload(self.model.servidores)
            )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_rut(self, rut: str) -> Optional[Empresa]:
        """
        Get empresa by RUT (tax ID).

        Args:
            rut: RUT/Tax ID

        Returns:
            Empresa if found, None otherwise
        """
        query = select(self.model).where(
            self.model.rut == rut
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def search_empresas(
        self,
        search_term: str,
        estado: Optional[str] = None,
        es_cliente: Optional[bool] = None,
        es_proveedor: Optional[bool] = None,
        es_partner: Optional[bool] = None
    ) -> List[Empresa]:
        """
        Search empresas with filters.

        Args:
            search_term: Term to search in nombre, nombre_comercial, razon_social
            estado: Filter by estado (activo, inactivo, prospecto, cliente)
            es_cliente: Filter by cliente status
            es_proveedor: Filter by proveedor status
            es_partner: Filter by partner status

        Returns:
            List of matching empresas
        """
        conditions = [
            self.model.is_active == True
        ]

        # Search term
        if search_term:
            pattern = f"%{search_term}%"
            conditions.append(
                or_(
                    self.model.nombre.ilike(pattern),
                    self.model.nombre_comercial.ilike(pattern),
                    self.model.razon_social.ilike(pattern),
                    self.model.rut.ilike(pattern)
                )
            )

        # Estado filter
        if estado:
            conditions.append(self.model.estado == estado)

        # Type filters
        if es_cliente is not None:
            conditions.append(self.model.es_cliente == es_cliente)
        if es_proveedor is not None:
            conditions.append(self.model.es_proveedor == es_proveedor)
        if es_partner is not None:
            conditions.append(self.model.es_partner == es_partner)

        query = select(self.model).where(
            and_(*conditions)
        ).order_by(self.model.nombre)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_empresas_by_industria(
        self,
        industria: str
    ) -> List[Empresa]:
        """
        Get empresas by industry.

        Args:
            industria: Industry name

        Returns:
            List of empresas in that industry
        """
        query = select(self.model).where(
            and_(
                self.model.industria == industria,
                self.model.is_active == True
            )
        ).order_by(self.model.nombre)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_empresas_by_location(
        self,
        country_id: Optional[int] = None,
        state_id: Optional[int] = None,
        city_id: Optional[int] = None
    ) -> List[Empresa]:
        """
        Get empresas by location.

        Args:
            country_id: Country filter
            state_id: State filter
            city_id: City filter

        Returns:
            List of empresas in that location
        """
        conditions = [
            self.model.is_active == True
        ]

        if country_id:
            conditions.append(self.model.country_id == country_id)
        if state_id:
            conditions.append(self.model.state_id == state_id)
        if city_id:
            conditions.append(self.model.city_id == city_id)

        query = select(self.model).where(
            and_(*conditions)
        ).order_by(self.model.nombre)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_empresas_with_servidores(self) -> List[Empresa]:
        """
        Get empresas that have servers.

        Returns:
            List of empresas with servers
        """
        from src.models.infrastructure.servidor import Servidor

        query = (
            select(self.model)
            .join(Servidor, Servidor.empresa_id == self.model.id)
            .where(self.model.is_active == True)
            .options(selectinload(self.model.servidores))
            .distinct()
            .order_by(self.model.nombre)
        )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_empresa_statistics(self) -> Dict[str, Any]:
        """
        Get empresa statistics.

        Returns:
            Dictionary with statistics
        """
        # Total empresas
        total_query = select(func.count(self.model.id)).where(
            self.model.is_active == True
        )
        total_result = await self._session.execute(total_query)
        total = total_result.scalar()

        # By type
        clientes_query = select(func.count(self.model.id)).where(
            and_(
                self.model.is_active == True,
                self.model.es_cliente == True
            )
        )
        clientes_result = await self._session.execute(clientes_query)
        clientes = clientes_result.scalar()

        proveedores_query = select(func.count(self.model.id)).where(
            and_(
                self.model.is_active == True,
                self.model.es_proveedor == True
            )
        )
        proveedores_result = await self._session.execute(proveedores_query)
        proveedores = proveedores_result.scalar()

        partners_query = select(func.count(self.model.id)).where(
            and_(
                self.model.is_active == True,
                self.model.es_partner == True
            )
        )
        partners_result = await self._session.execute(partners_query)
        partners = partners_result.scalar()

        # By estado
        estados_query = (
            select(
                self.model.estado,
                func.count(self.model.id).label('count')
            )
            .where(self.model.is_active == True)
            .group_by(self.model.estado)
        )
        estados_result = await self._session.execute(estados_query)
        estados = {row.estado: row.count for row in estados_result}

        return {
            'total': total,
            'clientes': clientes,
            'proveedores': proveedores,
            'partners': partners,
            'por_estado': estados
        }

    async def check_rut_exists(
        self,
        rut: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Check if RUT already exists.

        Args:
            rut: RUT to check
            exclude_id: ID to exclude from check (for updates)

        Returns:
            True if RUT exists
        """
        conditions = [self.model.rut == rut]

        if exclude_id:
            conditions.append(self.model.id != exclude_id)

        query = select(func.count(self.model.id)).where(
            and_(*conditions)
        )
        result = await self._session.execute(query)
        count = result.scalar()
        return count > 0