from sqlalchemy import String, Float, Text, ForeignKey, JSON, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone
from app.db.base import Base, TimestampMixin, generate_uuid

class OutreachMessage(Base, TimestampMixin):
    __tablename__ = "outreach_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    opportunity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("opportunities.id", ondelete="SET NULL"), index=True, nullable=True)
    contact_id: Mapped[str] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="CASCADE"), index=True, nullable=False)

    channel: Mapped[str] = mapped_column(String(50), default="LINKEDIN_CONNECT", nullable=False) # LINKEDIN_CONNECT, LINKEDIN_MESSAGE, EMAIL, REFERRAL_REQUEST, FOLLOW_UP
    strategy: Mapped[str] = mapped_column(String(50), default="RECRUITER", nullable=False) # RECRUITER, HIRING_MANAGER, EMPLOYEE, EXISTING_CONNECTION
    
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    personalization_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_used: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Status: NEW, DRAFT, APPROVED, SENT, REPLIED, POSITIVE, NEGATIVE, NO_RESPONSE, FOLLOW_UP_DUE, CLOSED
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", index=True, nullable=False)
    
    # Human approval audit fields
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    message_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="outreach_messages")
    opportunity = relationship("Opportunity", back_populates="outreach_messages")
    contact = relationship("Contact", back_populates="outreach_messages")
    events = relationship("OutreachEvent", back_populates="outreach_message", cascade="all, delete-orphan")
    followups = relationship("FollowUp", back_populates="outreach_message", cascade="all, delete-orphan")

class OutreachEvent(Base, TimestampMixin):
    __tablename__ = "outreach_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    outreach_id: Mapped[str] = mapped_column(String(36), ForeignKey("outreach_messages.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False) # GENERATED, EDITED, APPROVED, REJECTED, SENT, RESPONSE_LOGGED, FOLLOWUP_SCHEDULED
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    outreach_message = relationship("OutreachMessage", back_populates="events")
