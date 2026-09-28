from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MatchResultOut(BaseModel):
    id: str
    user_id: str
    opportunity_id: str
    overall_match_score: float
    role_match: float
    skill_match: float
    eligibility_match: float
    location_match: float
    experience_match: float
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    relevant_projects: List[str] = Field(default_factory=list)
    eligibility_reasoning: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class MatchRequest(BaseModel):
    opportunity_id: str
