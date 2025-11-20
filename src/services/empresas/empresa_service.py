"""Empresa service for business logic."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.empresas.empresa_repository import EmpresaRepository
from src.models.empresas.empresa import Empresa
from src.services.locations.location_service import LocationService


class EmpresaService:
    """Service for empresa-related business logic."""

    def __init__(self, session: AsyncSession):
        """
        Initialize empresa service.

        Args:
            session: Database session
        """
        self.session = session
        self.repository = EmpresaRepository(session)
        self.location_service = LocationService(session)

    async def create_empresa(
        self,
        nombre: str,
        rut: Optional[str] = None,
        tipo_empresa: Optional[str] = None,
        industria: Optional[str] = None,
        telefono_principal: Optional[str] = None,
        email_principal: Optional[str] = None,
        country_id: Optional[int] = None,
        state_id: Optional[int] = None,
        city_id: Optional[int] = None,
        direccion: Optional[str] = None,
        **kwargs
    ) -> Empresa:
        """
        Create a new empresa.

        Args:
            nombre: Company name
            rut: Tax ID
            tipo_empresa: Company type
            industria: Industry
            telefono_principal: Main phone
            email_principal: Main email
            country_id: Country ID
            state_id: State ID
            city_id: City ID
            direccion: Address
            **kwargs: Additional fields

        Returns:
            Created empresa

        Raises:
            ValueError: If RUT already exists or location is invalid
        """
        # Validate RUT uniqueness
        if rut:
            exists = await self.repository.check_rut_exists(rut)
            if exists:
                raise ValueError(f"Ya existe una empresa con RUT {rut}")

        # Validate location hierarchy
        if any([country_id, state_id, city_id]):
            location_validation = await self.location_service.validate_location_ids(
                country_id=country_id,
                state_id=state_id,
                city_id=city_id
            )
            if not location_validation['valid']:
                raise ValueError(f"Ubicación inválida: {', '.join(location_validation['errors'])}")

        # Create empresa
        empresa_data = {
            'nombre': nombre,
            'rut': rut,
            'tipo_empresa': tipo_empresa,
            'industria': industria,
            'telefono_principal': telefono_principal,
            'email_principal': email_principal,
            'country_id': country_id,
            'state_id': state_id,
            'city_id': city_id,
            'direccion': direccion,
            **kwargs
        }

        # Remove None values
        empresa_data = {k: v for k, v in empresa_data.items() if v is not None}

        return await self.repository.create(**empresa_data)

    async def get_empresa_by_id(
        self,
        empresa_id: int,
        include_relationships: bool = False
    ) -> Optional[Empresa]:
        """
        Get empresa by ID.

        Args:
            empresa_id: Empresa ID
            include_relationships: Whether to include related data

        Returns:
            Empresa if found, None otherwise
        """
        if include_relationships:
            empresas = await self.repository.get_all(
                skip=0,
                limit=1,
                filters={'id': empresa_id}
            )
            return empresas[0] if empresas else None

        return await self.repository.get(empresa_id)

    async def get_empresa_by_rut(self, rut: str) -> Optional[Empresa]:
        """
        Get empresa by RUT.

        Args:
            rut: RUT/Tax ID

        Returns:
            Empresa if found, None otherwise
        """
        return await self.repository.get_by_rut(rut)

    async def list_empresas(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        estado: Optional[str] = None,
        es_cliente: Optional[bool] = None,
        es_proveedor: Optional[bool] = None,
        es_partner: Optional[bool] = None
    ) -> List[Empresa]:
        """
        List empresas with optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term
            estado: Filter by estado
            es_cliente: Filter by cliente status
            es_proveedor: Filter by proveedor status
            es_partner: Filter by partner status

        Returns:
            List of empresas
        """
        if search or estado is not None or any([es_cliente, es_proveedor, es_partner]):
            empresas = await self.repository.search_empresas(
                search_term=search or '',
                estado=estado,
                es_cliente=es_cliente,
                es_proveedor=es_proveedor,
                es_partner=es_partner
            )
            # Apply pagination
            return empresas[skip:skip + limit]

        return await self.repository.get_all(skip=skip, limit=limit)

    async def update_empresa(
        self,
        empresa_id: int,
        **update_data
    ) -> Optional[Empresa]:
        """
        Update an empresa.

        Args:
            empresa_id: Empresa ID
            **update_data: Fields to update

        Returns:
            Updated empresa if found, None otherwise

        Raises:
            ValueError: If RUT already exists or location is invalid
        """
        # Get existing empresa
        empresa = await self.repository.get(empresa_id)
        if not empresa:
            return None

        # Validate RUT uniqueness if changed
        if 'rut' in update_data and update_data['rut'] != empresa.rut:
            exists = await self.repository.check_rut_exists(
                update_data['rut'],
                exclude_id=empresa_id
            )
            if exists:
                raise ValueError(f"Ya existe una empresa con RUT {update_data['rut']}")

        # Validate location if changed
        location_fields = ['country_id', 'state_id', 'city_id']
        if any(field in update_data for field in location_fields):
            country_id = update_data.get('country_id', empresa.country_id)
            state_id = update_data.get('state_id', empresa.state_id)
            city_id = update_data.get('city_id', empresa.city_id)

            if any([country_id, state_id, city_id]):
                location_validation = await self.location_service.validate_location_ids(
                    country_id=country_id,
                    state_id=state_id,
                    city_id=city_id
                )
                if not location_validation['valid']:
                    raise ValueError(f"Ubicación inválida: {', '.join(location_validation['errors'])}")

        # Update
        update_data['updated_at'] = datetime.utcnow()
        return await self.repository.update(empresa_id, **update_data)

    async def delete_empresa(self, empresa_id: int) -> bool:
        """
        Delete an empresa (soft delete by setting is_active=False).

        Args:
            empresa_id: Empresa ID

        Returns:
            True if deleted, False if not found
        """
        empresa = await self.repository.get(empresa_id)
        if not empresa:
            return False

        # Check if empresa has servers
        if empresa.servidores:
            raise ValueError(
                f"No se puede eliminar la empresa porque tiene {len(empresa.servidores)} servidor(es) asociado(s)"
            )

        # Soft delete
        await self.repository.update(empresa_id, is_active=False)
        return True

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
        return await self.repository.get_empresas_by_location(
            country_id=country_id,
            state_id=state_id,
            city_id=city_id
        )

    async def get_empresas_with_servidores(self) -> List[Empresa]:
        """
        Get empresas that have servers.

        Returns:
            List of empresas with servers
        """
        return await self.repository.get_empresas_with_servidores()

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get empresa statistics.

        Returns:
            Dictionary with statistics
        """
        return await self.repository.get_empresa_statistics()

    async def mark_as_cliente(self, empresa_id: int) -> Optional[Empresa]:
        """
        Mark empresa as cliente.

        Args:
            empresa_id: Empresa ID

        Returns:
            Updated empresa if found
        """
        return await self.repository.update(
            empresa_id,
            es_cliente=True,
            estado='activo',
            fecha_inicio_relacion=datetime.utcnow()
        )

    async def mark_as_proveedor(self, empresa_id: int) -> Optional[Empresa]:
        """
        Mark empresa as proveedor.

        Args:
            empresa_id: Empresa ID

        Returns:
            Updated empresa if found
        """
        return await self.repository.update(
            empresa_id,
            es_proveedor=True,
            estado='activo'
        )

    async def mark_as_partner(self, empresa_id: int) -> Optional[Empresa]:
        """
        Mark empresa as partner.

        Args:
            empresa_id: Empresa ID

        Returns:
            Updated empresa if found
        """
        return await self.repository.update(
            empresa_id,
            es_partner=True,
            estado='activo'
        )

    async def get_empresa_full_info(self, empresa_id: int) -> Dict[str, Any]:
        """
        Get complete empresa information including relationships.

        Args:
            empresa_id: Empresa ID

        Returns:
            Dictionary with empresa info and relationships
        """
        empresa = await self.get_empresa_by_id(empresa_id, include_relationships=True)
        if not empresa:
            return None

        # Get location hierarchy
        location_info = await self.location_service.get_location_hierarchy(
            country_id=empresa.country_id,
            state_id=empresa.state_id,
            city_id=empresa.city_id
        )

        return {
            'empresa': empresa.to_dict(),
            'location': location_info,
            'servidores': [s.to_dict() for s in empresa.servidores] if empresa.servidores else [],
            'tipo_relacion': empresa.tipo_relacion,
            'direccion_completa': empresa.direccion_completa
        }