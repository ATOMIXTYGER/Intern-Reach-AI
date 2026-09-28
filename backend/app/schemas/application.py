from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ApplicationBase(BaseModel):
    opportunity_id: Optional[str] = None
    company_name: str
    role_title: str
    application_url: Optional[str] = None
    date_applied: Optional[datetime] = None
    status: str = Field(default="SAVED", description="SAVED, APPLIED, OA, INTERVIEW, FINAL_ROUND, OFFER, REJECTED, WITHDRAWN")
    referral_contact_id: Optional[str] = None
    recruiter_contact_id: Optional[str] = None
    interview_stage: Optional[str] = None
    next_action: Optional[str] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    date_applied: Optional[datetime] = None
    referral_contact_id: Optional[str] = None
    recruiter_contact_id: Optional[str] = None
    interview_stage: Optional[str] = None
    next_action: Optional[str] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None

class ApplicationOut(ApplicationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
