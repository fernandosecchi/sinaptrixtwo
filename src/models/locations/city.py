"""City model for geographic data."""
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.locations.country import Country
    from src.models.locations.state import State
    from src.models.leads.lead import Lead


class City(Base, TimestampMixin):
    """City model for major cities in America."""

    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    state_id: Mapped[int] = mapped_column(
        ForeignKey("states.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name_ascii: Mapped[Optional[str]] = mapped_column(String(100))  # ASCII version
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8))
    population: Mapped[Optional[int]] = mapped_column(Integer, index=True)  # Approximate population
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    is_capital: Mapped[bool] = mapped_column(Boolean, default=False)  # State capital
    is_national_capital: Mapped[bool] = mapped_column(Boolean, default=False)  # Country capital
    is_major_city: Mapped[bool] = mapped_column(Boolean, default=False)  # Major city flag
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    country: Mapped["Country"] = relationship(
        "Country",
        foreign_keys=[country_id]
    )

    state: Mapped["State"] = relationship(
        "State",
        back_populates="cities"
    )

    leads: Mapped[List["Lead"]] = relationship(
        "Lead",
        back_populates="city",
        foreign_keys="Lead.city_id"
    )

    def __repr__(self) -> str:
        return f"<City(name='{self.name}', state_id={self.state_id})>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "state_id": self.state_id,
            "country_id": self.country_id,
            "name": self.name,
            "name_ascii": self.name_ascii,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "population": self.population,
            "is_capital": self.is_capital,
            "is_major_city": self.is_major_city,
            "is_active": self.is_active
        }