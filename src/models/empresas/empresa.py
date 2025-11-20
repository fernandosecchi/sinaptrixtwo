"""Empresa model for company/organization management."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.infrastructure.servidor import Servidor
    from src.models.locations.country import Country
    from src.models.locations.state import State
    from src.models.locations.city import City
    from src.models.leads.lead import Lead


class Empresa(Base, TimestampMixin):
    """
    Empresa model for managing companies/organizations.

    This is a central entity that can own servers, have contacts,
    leads, and other related business entities.
    """

    __tablename__ = "empresas"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Basic Information
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    nombre_comercial: Mapped[Optional[str]] = mapped_column(String(200))
    razon_social: Mapped[Optional[str]] = mapped_column(String(200))

    # Tax/Legal Information
    rut: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True)  # RUT/Tax ID
    tipo_empresa: Mapped[Optional[str]] = mapped_column(String(50))  # SA, SRL, etc.

    # Industry/Business
    industria: Mapped[Optional[str]] = mapped_column(String(100))  # Banking, Retail, etc.
    sector: Mapped[Optional[str]] = mapped_column(String(100))  # Private, Public, etc.
    tamanio: Mapped[Optional[str]] = mapped_column(String(50))  # Small, Medium, Large, Enterprise
    num_empleados: Mapped[Optional[int]] = mapped_column()
    facturacion_anual: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))

    # Contact Information
    telefono_principal: Mapped[Optional[str]] = mapped_column(String(20))
    telefono_secundario: Mapped[Optional[str]] = mapped_column(String(20))
    email_principal: Mapped[Optional[str]] = mapped_column(String(255))
    email_facturacion: Mapped[Optional[str]] = mapped_column(String(255))
    sitio_web: Mapped[Optional[str]] = mapped_column(String(255))

    # Location (using our location tables)
    country_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("countries.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    state_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("states.id", ondelete="SET NULL"),
        nullable=True
    )
    city_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cities.id", ondelete="SET NULL"),
        nullable=True
    )

    # Address Details
    direccion: Mapped[Optional[str]] = mapped_column(String(255))
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(20))

    # Additional Information
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    notas: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    estado: Mapped[str] = mapped_column(
        String(20),
        default='activo',
        nullable=False,
        index=True
    )  # activo, inactivo, prospecto, cliente

    es_cliente: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    es_proveedor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    es_partner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Important Dates
    fecha_inicio_relacion: Mapped[Optional[datetime]] = mapped_column(DateTime)
    fecha_fin_relacion: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Audit
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    servidores: Mapped[List["Servidor"]] = relationship(
        "Servidor",
        back_populates="empresa",
        cascade="all, delete-orphan"
    )

    country: Mapped[Optional["Country"]] = relationship(
        "Country",
        foreign_keys=[country_id]
    )

    state: Mapped[Optional["State"]] = relationship(
        "State",
        foreign_keys=[state_id]
    )

    city: Mapped[Optional["City"]] = relationship(
        "City",
        foreign_keys=[city_id]
    )

    # Future relationships (commented for now)
    # contactos: Mapped[List["Contacto"]] = relationship(
    #     "Contacto",
    #     back_populates="empresa",
    #     cascade="all, delete-orphan"
    # )

    # leads: Mapped[List["Lead"]] = relationship(
    #     "Lead",
    #     back_populates="empresa",
    #     foreign_keys="Lead.empresa_id"
    # )

    def __repr__(self) -> str:
        return f"<Empresa(id={self.id}, nombre='{self.nombre}', rut='{self.rut}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "nombre_comercial": self.nombre_comercial,
            "razon_social": self.razon_social,
            "rut": self.rut,
            "tipo_empresa": self.tipo_empresa,
            "industria": self.industria,
            "sector": self.sector,
            "tamanio": self.tamanio,
            "num_empleados": self.num_empleados,
            "telefono_principal": self.telefono_principal,
            "email_principal": self.email_principal,
            "sitio_web": self.sitio_web,
            "direccion": self.direccion,
            "estado": self.estado,
            "es_cliente": self.es_cliente,
            "es_proveedor": self.es_proveedor,
            "es_partner": self.es_partner,
            "country_id": self.country_id,
            "state_id": self.state_id,
            "city_id": self.city_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def direccion_completa(self) -> str:
        """Get complete formatted address."""
        parts = []
        if self.direccion:
            parts.append(self.direccion)
        if self.city:
            parts.append(self.city.name)
        if self.state:
            parts.append(self.state.name)
        if self.country:
            parts.append(self.country.name)
        if self.codigo_postal:
            parts.append(f"CP: {self.codigo_postal}")
        return ", ".join(parts)

    @property
    def tipo_relacion(self) -> str:
        """Get relationship type as string."""
        tipos = []
        if self.es_cliente:
            tipos.append("Cliente")
        if self.es_proveedor:
            tipos.append("Proveedor")
        if self.es_partner:
            tipos.append("Partner")
        return " / ".join(tipos) if tipos else "Prospecto"