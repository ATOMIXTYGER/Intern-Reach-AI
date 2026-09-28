from sqlalchemy import String, Float, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone
from app.db.base import Base, TimestampMixin, generate_uuid

class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    company_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    current_title: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    public_profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="public_web", nullable=False)
    
    # Operational relevance: high, medium, low, unknown
    operational_relevance: Mapped[str] = mapped_column(String(50), default="unknown", nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    relevance_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    company = relationship("Company", back_populates="contacts")
    evidence = relationship("ContactEvidence", back_populates="contact", cascade="all, delete-orphan")
    opportunities = relationship("OpportunityContact", back_populates="contact", cascade="all, delete-orphan")
    outreach_messages = relationship("OutreachMessage", back_populates="contact", cascade="all, delete-orphan")

class ContactEvidence(Base, TimestampMixin):
    __tablename__ = "contact_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "company_careers_page", "public_post", "university_relations"
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    date_observed: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    contact = relationship("Contact", back_populates="evidence")

class OpportunityContact(Base, TimestampMixin):
    __tablename__ = "opportunity_contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), index=True, nullable=False)
    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), index=True, nullable=False)
    relevance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    opportunity = relationship("Opportunity", back_populates="contacts")
    contact = relationship("Contact", back_populates="opportunities")
