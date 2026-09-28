from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.contact import ContactOut
from app.schemas.opportunity import OpportunityOut

class LLMMessageResponse(BaseModel):
    message: str
    personalization_reason: str
    evidence_used: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

class OutreachGenerateRequest(BaseModel):
    opportunity_id: Optional[str] = None
    contact_id: str
    channel: str = Field(default="LINKEDIN_CONNECT", description="'LINKEDIN_CONNECT', 'LINKEDIN_MESSAGE', 'EMAIL', 'REFERRAL_REQUEST', 'FOLLOW_UP'")
    strategy: str = Field(default="RECRUITER", description="'RECRUITER', 'HIRING_MANAGER', 'EMPLOYEE', 'EXISTING_CONNECTION'")

class OutreachUpdate(BaseModel):
    content: Optional[str] = None
    subject: Optional[str] = None
    channel: Optional[str] = None
    strategy: Optional[str] = None
    notes: Optional[str] = None

class OutreachApproveRequest(BaseModel):
    approved_by: Optional[str] = None
    edited_content: Optional[str] = None

class OutreachStatusUpdate(BaseModel):
    status: str = Field(..., description="NEW, DRAFT, APPROVED, SENT, REPLIED, POSITIVE, NEGATIVE, NO_RESPONSE, FOLLOW_UP_DUE, CLOSED")
    notes: Optional[str] = None

class OutreachOut(BaseModel):
    id: str
    user_id: str
    opportunity_id: Optional[str] = None
    contact_id: str
    channel: str
    strategy: str
    subject: Optional[str] = None
    content: str
    personalization_reason: Optional[str] = None
    evidence_used: List[str] = Field(default_factory=list)
    confidence: float
    status: str
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    sent_at: Optional[datetime] = None
    last_contacted_at: Optional[datetime] = None
    message_version: int
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    contact: Optional[ContactOut] = None
    opportunity: Optional[OpportunityOut] = None

    class Config:
        from_attributes = True

class DuplicateCheckResult(BaseModel):
    has_contacted_person: bool
    has_contacted_company_recently: bool
    has_contacted_for_opportunity: bool
    warnings: List[str] = Field(default_factory=list)
