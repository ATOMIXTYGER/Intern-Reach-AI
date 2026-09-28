from sqlalchemy import String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin, generate_uuid

class CandidateProfile(Base, TimestampMixin):
    __tablename__ = "candidate_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    
    # Personal
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    university: Mapped[str] = mapped_column(String(255), nullable=True)
    degree: Mapped[str] = mapped_column(String(255), nullable=True)
    graduation_year: Mapped[int] = mapped_column(Integer, default=2028, nullable=False, index=True)
    current_year: Mapped[str] = mapped_column(String(50), default="Sophomore / 2nd Year", nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)
    preferred_locations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # Career Preferences
    target_roles: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    target_industries: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    target_companies: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    preferred_company_sizes: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    preferred_internship_duration: Mapped[str] = mapped_column(String(100), default="2-6 months", nullable=True)
    remote_preference: Mapped[str] = mapped_column(String(50), default="Hybrid / Remote / On-site", nullable=True)

    # Technical Skills { "languages": [], "frameworks": [], "databases": [], "cloud": [], "ai_ml": [], "tools": [] }
    skills: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Experiences { "internships": [], "projects": [], "research": [], "achievements": [], "leadership": [], "certifications": [] }
    experiences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Raw / Structured Resume Summary
    raw_resume_text: Mapped[str] = mapped_column(Text, nullable=True)
    structured_resume: Mapped[dict] = mapped_column(JSON, default=dict, nullable=True)

    # Relationship
    user = relationship("User", back_populates="candidate_profile")

class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    structured_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    user = relationship("User", back_populates="resumes")
