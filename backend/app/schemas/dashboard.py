from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.opportunity import OpportunityOut
from app.schemas.outreach import OutreachOut

class DashboardStats(BaseModel):
    new_opportunities: int = 0
    eligible_opportunities: int = 0
    high_match_opportunities: int = 0
    contacts_researched: int = 0
    draft_messages: int = 0
    awaiting_approval: int = 0
    messages_sent: int = 0
    responses: int = 0
    positive_responses: int = 0
    referrals: int = 0
    interviews: int = 0

class ActionableOpportunity(BaseModel):
    id: str
    company_name: str
    title: str
    location: str
    deadline: Optional[datetime] = None
    eligibility_status: str
    match_score: float
    has_contact: bool
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_id: Optional[str] = None
    outreach_status: Optional[str] = None # DRAFT, APPROVED, SENT, etc.
    application_status: Optional[str] = None
    application_url: str

class AnalyticsData(BaseModel):
    applications_by_status: Dict[str, int] = Field(default_factory=dict)
    outreach_by_status: Dict[str, int] = Field(default_factory=dict)
    response_rate_percent: float = 0.0
    positive_response_rate_percent: float = 0.0
    interviews_count: int = 0
    referrals_count: int = 0
    top_target_companies: List[Dict[str, Any]] = Field(default_factory=list)
    top_roles: List[Dict[str, Any]] = Field(default_factory=list)
    sources_distribution: Dict[str, int] = Field(default_factory=dict)
