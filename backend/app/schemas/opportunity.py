from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class VerificationResult(BaseModel):
    verified: bool
    eligibility: str = Field(description="'eligible', 'possibly_eligible', 'not_eligible', 'unknown'")
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)

class OpportunityBase(BaseModel):
    company_name: str
    title: str
    job_description: str
    location: str
    internship_duration: Optional[str] = None
    application_url: str
    source: str = "public_web"
    deadline: Optional[datetime] = None
    graduation_eligibility: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    employment_type: str = "Internship"
    evidence_url: Optional[str] = None

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    job_description: Optional[str] = None
    location: Optional[str] = None
    internship_duration: Optional[str] = None
    application_url: Optional[str] = None
    deadline: Optional[datetime] = None
    graduation_eligibility: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    is_active: Optional[bool] = None

class OpportunityOut(OpportunityBase):
    id: str
    company_id: Optional[str] = None
    date_discovered: datetime
    verified: bool
    eligibility_status: str
    verification_confidence: float
    verification_reasons: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OpportunitySearchRequest(BaseModel):
    target_roles: Optional[List[str]] = None
    graduation_year: Optional[int] = 2028
    locations: Optional[List[str]] = None
    target_companies: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    keywords: Optional[str] = None
