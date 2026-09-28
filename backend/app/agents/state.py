from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentPipelineError(BaseModel):
    step: str
    error_message: str
    timestamp: str

class PipelineState(BaseModel):
    # Context
    user_id: str
    graduation_year: int = 2028
    target_roles: List[str] = Field(default_factory=list)
    target_locations: List[str] = Field(default_factory=list)
    target_companies: List[str] = Field(default_factory=list)
    skills: Dict[str, Any] = Field(default_factory=dict)
    experiences: Dict[str, Any] = Field(default_factory=dict)

    # Discovered & Verified
    raw_discovered: List[Dict[str, Any]] = Field(default_factory=list)
    deduplicated_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    verified_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    eligible_opportunities: List[Dict[str, Any]] = Field(default_factory=list)

    # Research & Matching
    researched_contacts: List[Dict[str, Any]] = Field(default_factory=list)
    matches: List[Dict[str, Any]] = Field(default_factory=list)

    # Generated Output
    outreach_drafts: List[Dict[str, Any]] = Field(default_factory=list)
    validated_drafts: List[Dict[str, Any]] = Field(default_factory=list)
    awaiting_human_approval: bool = True

    # Audit & Diagnostics
    logs: List[str] = Field(default_factory=list)
    errors: List[AgentPipelineError] = Field(default_factory=list)
