"""Service for Servidor iSeries management."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.infrastructure.servidor_repository import ServidorRepository
from src.models.infrastructure.servidor import (
    Servidor,
    ProcessorTier,
    EstadoRegistro,
    TipoStorage
)


class ServidorService:
    """Service for managing Servidor iSeries business logic."""

    def __init__(self, session: AsyncSession):
        """Initialize the service."""
        self.repository = ServidorRepository(session)
        self.session = session

    async def create_servidor(
        self,
        modelo: str,
        processor_feature_code: str,
        processor_tier: ProcessorTier = ProcessorTier.P10,
        nombre_servidor: Optional[str] = None,
        descripcion: Optional[str] = None,
        ubicacion: Optional[str] = None,
        es_virtualizado: bool = False,
        estado_registro: EstadoRegistro = EstadoRegistro.PRELIMINAR,
        numero_serie: Optional[str] = None,
        machine_type: Optional[str] = None,
        frame_id: Optional[str] = None,
        firmware_version: Optional[str] = None,
        cantidad_procesadores_fisicos: Optional[int] = None,
        memoria_total_mb: Optional[int] = None,
        tipo_storage: Optional[TipoStorage] = None,
        os_version: Optional[str] = None,
        ip_principal: Optional[str] = None,
        activo: bool = True,
        notas: Optional[str] = None
    ) -> Servidor:
        """
        Create a new servidor with validation.

        Args:
            modelo: Required server model
            processor_feature_code: Required processor feature code
            processor_tier: Processor tier level
            Other fields as defined in the model

        Returns:
            Created servidor instance

        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not modelo:
            raise ValueError("El modelo del servidor es obligatorio")

        if not processor_feature_code:
            raise ValueError("El código de característica del procesador es obligatorio")

        # Check for duplicate serial number if provided
        if numero_serie:
            if await self.repository.check_duplicate_serial(numero_serie):
                raise ValueError(f"Ya existe un servidor con el número de serie {numero_serie}")

        # Validate processor tier
        if processor_tier not in ProcessorTier:
            raise ValueError(f"Nivel de procesador inválido: {processor_tier}")

        # Validate estado
        if estado_registro not in EstadoRegistro:
            raise ValueError(f"Estado de registro inválido: {estado_registro}")

        # Create servidor
        servidor = await self.repository.create(
            modelo=modelo,
            processor_feature_code=processor_feature_code,
            processor_tier=processor_tier,
            nombre_servidor=nombre_servidor,
            descripcion=descripcion,
            ubicacion=ubicacion,
            es_virtualizado=es_virtualizado,
            estado_registro=estado_registro,
            numero_serie=numero_serie,
            machine_type=machine_type,
            frame_id=frame_id,
            firmware_version=firmware_version,
            cantidad_procesadores_fisicos=cantidad_procesadores_fisicos,
            memoria_total_mb=memoria_total_mb,
            tipo_storage=tipo_storage,
            os_version=os_version,
            ip_principal=ip_principal,
            activo=activo,
            notas=notas
        )

        return servidor

    async def update_servidor(
        self,
        servidor_id: int,
        **update_data
    ) -> Optional[Servidor]:
        """
        Update a servidor with validation.

        Args:
            servidor_id: ID of the servidor to update
            **update_data: Fields to update

        Returns:
            Updated servidor or None if not found

        Raises:
            ValueError: If validation fails
        """
        # Get existing servidor
        servidor = await self.repository.get(servidor_id)
        if not servidor:
            return None

        # Validate serial number uniqueness if being changed
        if 'numero_serie' in update_data and update_data['numero_serie']:
            if update_data['numero_serie'] != servidor.numero_serie:
                if await self.repository.check_duplicate_serial(
                    update_data['numero_serie'],
                    exclude_id=servidor_id
                ):
                    raise ValueError(f"Ya existe un servidor con el número de serie {update_data['numero_serie']}")

        # Validate enums if provided
        if 'processor_tier' in update_data:
            tier = update_data['processor_tier']
            if isinstance(tier, str):
                try:
                    update_data['processor_tier'] = ProcessorTier(tier)
                except ValueError:
                    raise ValueError(f"Nivel de procesador inválido: {tier}")

        if 'estado_registro' in update_data:
            estado = update_data['estado_registro']
            if isinstance(estado, str):
                try:
                    update_data['estado_registro'] = EstadoRegistro(estado)
                except ValueError:
                    raise ValueError(f"Estado de registro inválido: {estado}")

        if 'tipo_storage' in update_data:
            tipo = update_data['tipo_storage']
            if isinstance(tipo, str) and tipo:
                try:
                    update_data['tipo_storage'] = TipoStorage(tipo)
                except ValueError:
                    raise ValueError(f"Tipo de storage inválido: {tipo}")

        # Update servidor
        return await self.repository.update(servidor_id, **update_data)

    async def delete_servidor(self, servidor_id: int) -> bool:
        """
        Delete a servidor (soft delete by marking as inactive).

        Args:
            servidor_id: ID of the servidor to delete

        Returns:
            True if deleted, False if not found
        """
        servidor = await self.repository.get(servidor_id)
        if not servidor:
            return False

        # Instead of hard delete, mark as inactive and obsolete
        await self.repository.update(
            servidor_id,
            activo=False,
            estado_registro=EstadoRegistro.OBSOLETO
        )
        return True

    async def get_servidor(self, servidor_id: int) -> Optional[Servidor]:
        """Get a servidor by ID."""
        return await self.repository.get(servidor_id)

    async def get_servidor_by_serial(self, numero_serie: str) -> Optional[Servidor]:
        """Get a servidor by serial number."""
        return await self.repository.get_by_serial_number(numero_serie)

    async def list_servidores(
        self,
        skip: int = 0,
        limit: int = 100,
        activo_only: bool = False
    ) -> List[Servidor]:
        """
        List servidores with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            activo_only: If True, return only active servers

        Returns:
            List of servidores
        """
        if activo_only:
            return await self.repository.get_active_servers()
        return await self.repository.get_all(skip=skip, limit=limit)

    async def search_servidores(
        self,
        query: Optional[str] = None,
        modelo: Optional[str] = None,
        processor_tier: Optional[str] = None,
        estado: Optional[str] = None,
        activo: Optional[bool] = None,
        es_virtualizado: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Servidor]:
        """
        Search servidores with filters.

        Args:
            query: Text search
            modelo: Filter by model
            processor_tier: Filter by processor tier (as string)
            estado: Filter by status (as string)
            activo: Filter by active status
            es_virtualizado: Filter by virtualization
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            List of matching servidores
        """
        # Convert string enums to enum types
        tier_enum = None
        if processor_tier:
            try:
                tier_enum = ProcessorTier(processor_tier)
            except ValueError:
                pass  # Invalid tier, will return empty results

        estado_enum = None
        if estado:
            try:
                estado_enum = EstadoRegistro(estado)
            except ValueError:
                pass  # Invalid estado, will return empty results

        return await self.repository.search_servers(
            query=query,
            modelo=modelo,
            processor_tier=tier_enum,
            estado=estado_enum,
            activo=activo,
            es_virtualizado=es_virtualizado,
            skip=skip,
            limit=limit
        )

    async def get_statistics(self) -> Dict[str, Any]:
        """Get servidor statistics."""
        return await self.repository.get_statistics()

    async def bulk_update_status(
        self,
        servidor_ids: List[int],
        estado: EstadoRegistro
    ) -> int:
        """
        Update status for multiple servidores.

        Args:
            servidor_ids: List of servidor IDs to update
            estado: New status to apply

        Returns:
            Number of servidores updated
        """
        count = 0
        for servidor_id in servidor_ids:
            servidor = await self.repository.update(
                servidor_id,
                estado_registro=estado
            )
            if servidor:
                count += 1
        return count

    async def validate_quotation_fields(self, servidor_id: int) -> Dict[str, Any]:
        """
        Validate that a servidor has all required fields for quotation.

        Args:
            servidor_id: ID of the servidor to validate

        Returns:
            Dictionary with validation results
        """
        servidor = await self.repository.get(servidor_id)
        if not servidor:
            return {"valid": False, "errors": ["Servidor no encontrado"]}

        errors = []
        warnings = []

        # Required fields for quotation
        if not servidor.modelo:
            errors.append("Modelo es obligatorio para cotización")

        if not servidor.processor_feature_code:
            errors.append("Código de característica del procesador es obligatorio")

        if not servidor.processor_tier:
            errors.append("Nivel de procesador es obligatorio")

        # Recommended fields for complete quotation
        if not servidor.ubicacion:
            warnings.append("Ubicación no especificada")

        if servidor.es_virtualizado and not servidor.cantidad_procesadores_fisicos:
            warnings.append("Cantidad de procesadores físicos no especificada para servidor virtualizado")

        if not servidor.memoria_total_mb:
            warnings.append("Memoria total no especificada")

        # Status check
        if servidor.estado_registro == EstadoRegistro.PRELIMINAR:
            warnings.append("El registro está en estado preliminar")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "servidor": servidor.to_dict() if servidor else None
        }