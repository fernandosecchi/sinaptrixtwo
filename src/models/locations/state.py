"""State/Province model for geographic data."""
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.locations.country import Country
    from src.models.locations.city import City
    from src.models.leads.lead import Lead


class State(Base, TimestampMixin):
    """State/Province/Department model."""

    __tablename__ = "states"
    __table_args__ = (
        UniqueConstraint('country_id', 'code', name='uq_state_country_code'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    code: Mapped[str] = mapped_column(String(10), nullable=False)  # State/Province code
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name_ascii: Mapped[Optional[str]] = mapped_column(String(100))  # ASCII version (without accents)
    type: Mapped[Optional[str]] = mapped_column(String(20))  # state, province, department, region...
    capital: Mapped[Optional[str]] = mapped_column(String(100))  # State capital
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    country: Mapped["Country"] = relationship(
        "Country",
        back_populates="states"
    )

    cities: Mapped[List["City"]] = relationship(
        "City",
        back_populates="state",
        cascade="all, delete-orphan"
    )

    leads: Mapped[List["Lead"]] = relationship(
        "Lead",
        back_populates="state",
        foreign_keys="Lead.state_id"
    )

    def __repr__(self) -> str:
        return f"<State(code='{self.code}', name='{self.name}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "country_id": self.country_id,
            "code": self.code,
            "name": self.name,
            "name_ascii": self.name_ascii,
            "type": self.type,
            "capital": self.capital,
            "is_active": self.is_active
        }