"""Lead model for sales pipeline management."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base
from src.models.enums import LeadStatus, LeadSource

if TYPE_CHECKING:
    from src.models.locations.country import Country
    from src.models.locations.state import State
    from src.models.locations.city import City


class Lead(Base):
    """Lead model for sales pipeline."""
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Contact Information
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Location Information
    country_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("countries.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    state_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("states.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    city_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cities.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address_line1: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Lead Management
    status: Mapped[str] = mapped_column(
        String(20),
        default=LeadStatus.LEAD.value,
        nullable=False,
        index=True
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Additional Information
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    converted_to_prospect_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    converted_to_client_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    country: Mapped[Optional["Country"]] = relationship(
        "Country",
        back_populates="leads",
        foreign_keys=[country_id]
    )
    state: Mapped[Optional["State"]] = relationship(
        "State",
        back_populates="leads",
        foreign_keys=[state_id]
    )
    city: Mapped[Optional["City"]] = relationship(
        "City",
        back_populates="leads",
        foreign_keys=[city_id]
    )

    @property
    def full_name(self) -> str:
        """Return the full name of the lead."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.full_name}', status='{self.status}')>"