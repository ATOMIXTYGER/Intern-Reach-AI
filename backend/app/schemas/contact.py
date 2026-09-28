from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ContactEvidenceOut(BaseModel):
    id: str
    contact_id: str
    source_type: str
    source_url: str
    snippet: str
    date_observed: datetime
    confidence: float

    class Config:
        from_attributes = True

class ContactBase(BaseModel):
    name: str
    company_name: str
    current_title: str
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    public_profile_url: Optional[str] = None
    source: str = "public_web"
    operational_relevance: str = "unknown"
    relevance_score: float = 0.0
    confidence: float = 0.0
    relevance_reason: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactOut(ContactBase):
    id: str
    company_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    evidence: List[ContactEvidenceOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContactResearchRequest(BaseModel):
    company_name: str
    opportunity_id: Optional[str] = None
    target_roles: Optional[List[str]] = None
