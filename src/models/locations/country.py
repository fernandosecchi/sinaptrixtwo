"""Country model for geographic data."""
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.locations.state import State
    from src.models.leads.lead import Lead


class Country(Base, TimestampMixin):
    """Country model for American continent."""

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False, index=True)  # ISO 3166-1 alpha-2
    code3: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)  # ISO 3166-1 alpha-3
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # English name
    name_es: Mapped[Optional[str]] = mapped_column(String(100))  # Spanish name
    name_pt: Mapped[Optional[str]] = mapped_column(String(100))  # Portuguese name
    name_fr: Mapped[Optional[str]] = mapped_column(String(100))  # French name
    official_name: Mapped[Optional[str]] = mapped_column(String(200))  # Official country name
    phone_prefix: Mapped[Optional[str]] = mapped_column(String(10))  # +1, +52, +55...
    currency_code: Mapped[Optional[str]] = mapped_column(String(3))  # USD, CAD, MXN, BRL...
    continent: Mapped[str] = mapped_column(String(50), default='America', nullable=False)
    subregion: Mapped[Optional[str]] = mapped_column(String(50))  # North America, South America, Caribbean...
    capital: Mapped[Optional[str]] = mapped_column(String(100))  # Capital city name
    timezone: Mapped[Optional[str]] = mapped_column(String(50))  # Default timezone
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8))  # Country center point
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    states: Mapped[List["State"]] = relationship(
        "State",
        back_populates="country",
        cascade="all, delete-orphan"
    )

    leads: Mapped[List["Lead"]] = relationship(
        "Lead",
        back_populates="country",
        foreign_keys="Lead.country_id"
    )

    def __repr__(self) -> str:
        return f"<Country(code='{self.code}', name='{self.name}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "code": self.code,
            "code3": self.code3,
            "name": self.name,
            "name_es": self.name_es,
            "name_pt": self.name_pt,
            "phone_prefix": self.phone_prefix,
            "currency_code": self.currency_code,
            "subregion": self.subregion,
            "is_active": self.is_active
        }