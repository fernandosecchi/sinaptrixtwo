"""Lead model for sales pipeline management."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base
from src.models.enums import LeadStatus, LeadSource


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
    
    @property
    def full_name(self) -> str:
        """Return the full name of the lead."""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.full_name}', status='{self.status}')>"