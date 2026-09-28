from sqlalchemy import String, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.db.base import Base, TimestampMixin, generate_uuid

class MatchResult(Base, TimestampMixin):
    __tablename__ = "match_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Internal prioritization scores (0 - 100)
    overall_match_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    role_match: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    skill_match: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    eligibility_match: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    location_match: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    experience_match: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Detailed Analysis
    matched_skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    relevant_projects: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    eligibility_reasoning: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    concerns: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    opportunity = relationship("Opportunity", back_populates="match_results")
