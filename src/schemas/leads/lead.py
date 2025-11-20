"""Lead schemas for data validation and serialization."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from src.models.enums import LeadStatus, LeadSource


class LeadBase(BaseModel):
    """Base lead schema with common attributes."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('El teléfono debe contener solo números')
        return v


class LeadCreate(LeadBase):
    """Schema for creating a new lead."""
    source: Optional[LeadSource] = LeadSource.WEBSITE
    status: LeadStatus = LeadStatus.LEAD


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    source: Optional[LeadSource] = None


class LeadStatusUpdate(BaseModel):
    """Schema for updating lead status."""
    status: LeadStatus
    
    @field_validator('status')
    @classmethod
    def validate_status_transition(cls, v: LeadStatus) -> LeadStatus:
        """Validate status transitions."""
        # Add business logic for valid transitions
        return v


class LeadInDB(LeadBase):
    """Schema for lead in database."""
    id: int
    status: str
    source: Optional[str]
    created_at: datetime
    converted_to_prospect_at: Optional[datetime]
    converted_to_client_at: Optional[datetime]
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LeadResponse(LeadInDB):
    """Schema for lead response."""
    full_name: str
    days_in_pipeline: int
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def days_in_pipeline(self) -> int:
        """Calculate days in current status."""
        now = datetime.utcnow()
        if self.status == LeadStatus.CLIENT.value and self.converted_to_client_at:
            return (now - self.converted_to_client_at).days
        elif self.status == LeadStatus.PROSPECT.value and self.converted_to_prospect_at:
            return (now - self.converted_to_prospect_at).days
        return (now - self.created_at).days


class LeadStatistics(BaseModel):
    """Schema for lead statistics."""
    total: int
    leads: int
    prospects: int
    clients: int
    lost: int
    conversion_rate: float
    
    
class LeadList(BaseModel):
    """Schema for list of leads response."""
    leads: list[LeadResponse]
    statistics: LeadStatistics
    page: int = 1
    page_size: int = 20