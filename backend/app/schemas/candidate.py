from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class CandidateSkills(BaseModel):
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    ai_ml: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)

class CandidateExperiences(BaseModel):
    internships: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    research: List[Dict[str, Any]] = Field(default_factory=list)
    achievements: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)
    leadership: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)
    certifications: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)

class CandidateProfileBase(BaseModel):
    full_name: str
    university: Optional[str] = None
    degree: Optional[str] = None
    graduation_year: int = 2028
    current_year: Optional[str] = "Sophomore / 2nd Year"
    location: Optional[str] = None
    preferred_locations: List[str] = Field(default_factory=lambda: ["India", "Bengaluru", "Hyderabad", "Pune", "Remote"])
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    target_roles: List[str] = Field(default_factory=lambda: [
        "Software Engineering Intern",
        "SDE Intern",
        "Backend Engineering Intern",
        "AI/ML Engineering Intern"
    ])
    target_industries: List[str] = Field(default_factory=lambda: ["Technology", "Fintech", "AI/ML", "SaaS"])
    target_companies: List[str] = Field(default_factory=list)
    preferred_company_sizes: List[str] = Field(default_factory=lambda: ["Early-stage Startup", "Scaleup", "Enterprise"])
    preferred_internship_duration: Optional[str] = "2-6 months"
    remote_preference: Optional[str] = "Hybrid / Remote / On-site"

    skills: CandidateSkills = Field(default_factory=CandidateSkills)
    experiences: CandidateExperiences = Field(default_factory=CandidateExperiences)

class CandidateProfileCreate(CandidateProfileBase):
    pass

class CandidateProfileUpdate(CandidateProfileBase):
    pass

class CandidateProfileOut(CandidateProfileBase):
    id: str
    user_id: str
    raw_resume_text: Optional[str] = None
    structured_resume: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ResumeOut(BaseModel):
    id: str
    file_name: str
    file_size: int
    mime_type: str
    extracted_text: Optional[str] = None
    structured_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
