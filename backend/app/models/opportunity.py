from sqlalchemy import String, Boolean, Float, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone
from app.db.base import Base, TimestampMixin, generate_uuid

class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    careers_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    opportunities = relationship("Opportunity", back_populates="company", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")

class Opportunity(Base, TimestampMixin):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    company_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    internship_duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    application_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source: Mapped[str] = mapped_column(String(100), default="public_web", nullable=False)
    date_discovered: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    
    # Eligibility & Verification
    graduation_eligibility: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # e.g. "2027/2028 Graduates"
    required_skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    preferred_skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50), default="Internship", nullable=False)
    evidence_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Verification Agent Outputs
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    eligibility_status: Mapped[str] = mapped_column(String(50), default="unknown", nullable=False) # eligible, possibly_eligible, not_eligible, unknown
    verification_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    verification_reasons: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)

    # Relationships
    company = relationship("Company", back_populates="opportunities")
    contacts = relationship("OpportunityContact", back_populates="opportunity", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="opportunity", cascade="all, delete-orphan")
    outreach_messages = relationship("OutreachMessage", back_populates="opportunity", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="opportunity", cascade="all, delete-orphan")
