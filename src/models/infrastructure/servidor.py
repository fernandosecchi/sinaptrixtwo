"""Servidor iSeries model for infrastructure management."""
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin
import enum

if TYPE_CHECKING:
    from src.models.empresas.empresa import Empresa


class ProcessorTier(str, enum.Enum):
    """Processor tier levels for iSeries."""
    P05 = "P05"
    P10 = "P10"
    P20 = "P20"
    P30 = "P30"
    P40 = "P40"
    P50 = "P50"
    UNKNOWN = "UNKNOWN"


class EstadoRegistro(str, enum.Enum):
    """Registration status for servers."""
    PRELIMINAR = "preliminar"
    CONFIRMADO = "confirmado"
    REVISION = "revision"
    OBSOLETO = "obsoleto"


class TipoStorage(str, enum.Enum):
    """Storage types for iSeries servers."""
    INTERNO = "interno"
    EXTERNO = "externo"
    SAN = "SAN"
    NAS = "NAS"
    VSAN = "VSAN"
    MIXTO = "mixto"


class Servidor(Base, TimestampMixin):
    """
    Servidor iSeries model for managing IBM Power Systems infrastructure.

    This model contains both quotation-critical fields and technical details.
    """
    __tablename__ = "servidores"

    # ========== IDENTIFICACIÓN (Primary Fields) ==========
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_servidor: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Nombre identificativo del servidor"
    )
    descripcion: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción o alias del servidor (Ej: Prod, Backup)"
    )

    # ========== EMPRESA PROPIETARIA ==========
    empresa_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("empresas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID de la empresa propietaria del servidor"
    )

    # ========== DATOS DE HARDWARE (Quotation Critical) ==========
    modelo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Modelo del servidor (Ej: 9009-42A, 8203-E4A)"
    )
    processor_feature_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Código de característica del procesador (Ej: EP30, EPX5)"
    )
    processor_tier: Mapped[ProcessorTier] = mapped_column(
        SQLEnum(ProcessorTier),
        nullable=False,
        default=ProcessorTier.P10,
        comment="Nivel de procesador (P05, P10, P20, P30)"
    )

    # ========== INFORMACIÓN OPCIONAL COMERCIAL ==========
    ubicacion: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Ubicación física o lógica (Datacenter A, On-premise, Cloud)"
    )
    es_virtualizado: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si está virtualizado con PowerVM"
    )
    estado_registro: Mapped[EstadoRegistro] = mapped_column(
        SQLEnum(EstadoRegistro),
        default=EstadoRegistro.PRELIMINAR,
        nullable=False,
        comment="Estado del registro (preliminar, confirmado)"
    )

    # ========== CAMPOS TÉCNICOS (Important but not for quotation) ==========
    # Identificadores físicos
    numero_serie: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
        comment="Número de serie del chasis"
    )
    machine_type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Tipo de máquina (Ej: 9009)"
    )
    frame_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="ID del frame si hay varios"
    )

    # Compatible con análisis técnico
    firmware_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Versión del firmware"
    )
    cantidad_procesadores_fisicos: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Cantidad de procesadores físicos"
    )
    memoria_total_mb: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Memoria total en MB"
    )
    tipo_storage: Mapped[Optional[TipoStorage]] = mapped_column(
        SQLEnum(TipoStorage),
        nullable=True,
        comment="Tipo de almacenamiento"
    )

    # ========== CAMPOS ADICIONALES ÚTILES ==========
    # Información de sistema operativo
    os_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Versión del OS/400 o IBM i (Ej: V7R4M0)"
    )

    # Información de red
    ip_principal: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Dirección IP principal"
    )

    # Estado operativo
    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Indica si el servidor está activo"
    )

    # Notas y observaciones
    notas: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Notas adicionales o observaciones"
    )

    # ========== RELATIONSHIPS ==========
    empresa: Mapped[Optional["Empresa"]] = relationship(
        "Empresa",
        back_populates="servidores"
    )

    def __repr__(self):
        """String representation of the servidor."""
        return f"<Servidor(id={self.id}, nombre='{self.nombre_servidor}', modelo='{self.modelo}')>"

    def to_dict(self) -> dict:
        """Convert servidor to dictionary."""
        return {
            'id': self.id,
            'nombre_servidor': self.nombre_servidor,
            'descripcion': self.descripcion,
            'empresa_id': self.empresa_id,
            'modelo': self.modelo,
            'processor_feature_code': self.processor_feature_code,
            'processor_tier': self.processor_tier.value if self.processor_tier else None,
            'ubicacion': self.ubicacion,
            'es_virtualizado': self.es_virtualizado,
            'estado_registro': self.estado_registro.value if self.estado_registro else None,
            'numero_serie': self.numero_serie,
            'machine_type': self.machine_type,
            'frame_id': self.frame_id,
            'firmware_version': self.firmware_version,
            'cantidad_procesadores_fisicos': self.cantidad_procesadores_fisicos,
            'memoria_total_mb': self.memoria_total_mb,
            'tipo_storage': self.tipo_storage.value if self.tipo_storage else None,
            'os_version': self.os_version,
            'ip_principal': self.ip_principal,
            'activo': self.activo,
            'notas': self.notas,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def display_name(self) -> str:
        """Get display name for the servidor."""
        return self.nombre_servidor or f"Servidor {self.modelo}"

    @property
    def is_power9_or_newer(self) -> bool:
        """Check if servidor is Power9 or newer based on model."""
        # Power9 models typically start with 9009, 9080, etc.
        # Power10 models typically start with 9105, 9108, etc.
        if self.modelo:
            model_prefix = self.modelo.split('-')[0] if '-' in self.modelo else self.modelo[:4]
            return model_prefix in ['9009', '9080', '9105', '9108', '9123']
        return False

    @property
    def memory_gb(self) -> Optional[float]:
        """Get memory in GB."""
        if self.memoria_total_mb:
            return round(self.memoria_total_mb / 1024, 2)
        return None