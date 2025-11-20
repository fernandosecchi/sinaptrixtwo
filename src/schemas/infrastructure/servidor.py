"""Pydantic schemas for Servidor iSeries."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from src.models.infrastructure.servidor import ProcessorTier, EstadoRegistro, TipoStorage


class ServidorBase(BaseModel):
    """Base schema for Servidor."""
    nombre_servidor: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    modelo: str = Field(..., max_length=50, description="Modelo del servidor (Ej: 9009-42A)")
    processor_feature_code: str = Field(..., max_length=20, description="Código del procesador")
    processor_tier: ProcessorTier = Field(ProcessorTier.P10, description="Nivel de procesador")
    ubicacion: Optional[str] = Field(None, max_length=200)
    es_virtualizado: bool = Field(False, description="Indica si está virtualizado con PowerVM")
    estado_registro: EstadoRegistro = Field(EstadoRegistro.PRELIMINAR)
    numero_serie: Optional[str] = Field(None, max_length=50)
    machine_type: Optional[str] = Field(None, max_length=20)
    frame_id: Optional[str] = Field(None, max_length=50)
    firmware_version: Optional[str] = Field(None, max_length=50)
    cantidad_procesadores_fisicos: Optional[int] = Field(None, ge=1, le=256)
    memoria_total_mb: Optional[int] = Field(None, ge=1024)
    tipo_storage: Optional[TipoStorage] = None
    os_version: Optional[str] = Field(None, max_length=50)
    ip_principal: Optional[str] = Field(None, max_length=45)
    activo: bool = Field(True, description="Indica si el servidor está activo")
    notas: Optional[str] = None


class ServidorCreate(ServidorBase):
    """Schema for creating a Servidor."""
    pass


class ServidorUpdate(BaseModel):
    """Schema for updating a Servidor."""
    nombre_servidor: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    modelo: Optional[str] = Field(None, max_length=50)
    processor_feature_code: Optional[str] = Field(None, max_length=20)
    processor_tier: Optional[ProcessorTier] = None
    ubicacion: Optional[str] = Field(None, max_length=200)
    es_virtualizado: Optional[bool] = None
    estado_registro: Optional[EstadoRegistro] = None
    numero_serie: Optional[str] = Field(None, max_length=50)
    machine_type: Optional[str] = Field(None, max_length=20)
    frame_id: Optional[str] = Field(None, max_length=50)
    firmware_version: Optional[str] = Field(None, max_length=50)
    cantidad_procesadores_fisicos: Optional[int] = Field(None, ge=1, le=256)
    memoria_total_mb: Optional[int] = Field(None, ge=1024)
    tipo_storage: Optional[TipoStorage] = None
    os_version: Optional[str] = Field(None, max_length=50)
    ip_principal: Optional[str] = Field(None, max_length=45)
    activo: Optional[bool] = None
    notas: Optional[str] = None


class ServidorResponse(ServidorBase):
    """Schema for Servidor response."""
    id: int
    created_at: datetime
    updated_at: datetime
    display_name: str
    is_power9_or_newer: bool
    memory_gb: Optional[float]

    class Config:
        orm_mode = True
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM object."""
        data = {
            'id': obj.id,
            'nombre_servidor': obj.nombre_servidor,
            'descripcion': obj.descripcion,
            'modelo': obj.modelo,
            'processor_feature_code': obj.processor_feature_code,
            'processor_tier': obj.processor_tier,
            'ubicacion': obj.ubicacion,
            'es_virtualizado': obj.es_virtualizado,
            'estado_registro': obj.estado_registro,
            'numero_serie': obj.numero_serie,
            'machine_type': obj.machine_type,
            'frame_id': obj.frame_id,
            'firmware_version': obj.firmware_version,
            'cantidad_procesadores_fisicos': obj.cantidad_procesadores_fisicos,
            'memoria_total_mb': obj.memoria_total_mb,
            'tipo_storage': obj.tipo_storage,
            'os_version': obj.os_version,
            'ip_principal': obj.ip_principal,
            'activo': obj.activo,
            'notas': obj.notas,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'display_name': obj.display_name,
            'is_power9_or_newer': obj.is_power9_or_newer,
            'memory_gb': obj.memory_gb
        }
        return cls(**data)


class ServidorSearch(BaseModel):
    """Schema for searching Servidores."""
    query: Optional[str] = Field(None, description="Text search")
    modelo: Optional[str] = Field(None, description="Filter by model")
    processor_tier: Optional[ProcessorTier] = Field(None, description="Filter by processor tier")
    estado_registro: Optional[EstadoRegistro] = Field(None, description="Filter by status")
    activo: Optional[bool] = Field(None, description="Filter by active status")
    es_virtualizado: Optional[bool] = Field(None, description="Filter by virtualization")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")


class ServidorStatistics(BaseModel):
    """Schema for Servidor statistics."""
    total_servers: int
    active_servers: int
    virtualized_servers: int
    physical_servers: int
    servers_by_tier: dict
    servers_by_status: dict


class ServidorValidation(BaseModel):
    """Schema for validation results."""
    valid: bool
    errors: list[str]
    warnings: list[str]
    servidor: Optional[dict]