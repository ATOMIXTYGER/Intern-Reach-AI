from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime, timezone
from app.db.base import Base, TimestampMixin, generate_uuid

class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    opportunity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("opportunities.id", ondelete="SET NULL"), index=True, nullable=True)

    company_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    role_title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    application_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    date_applied: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Statuses: SAVED, APPLIED, OA, INTERVIEW, FINAL_ROUND, OFFER, REJECTED, WITHDRAWN
    status: Mapped[str] = mapped_column(String(50), default="SAVED", index=True, nullable=False)
    
    referral_contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    recruiter_contact_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)

    interview_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    next_action: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="applications")
    opportunity = relationship("Opportunity", back_populates="applications")
    referral_contact = relationship("Contact", foreign_keys=[referral_contact_id])
    recruiter_contact = relationship("Contact", foreign_keys=[recruiter_contact_id])
