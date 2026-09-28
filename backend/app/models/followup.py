from sqlalchemy import String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime, timezone
from app.db.base import Base, TimestampMixin, generate_uuid

class FollowUp(Base, TimestampMixin):
    __tablename__ = "followups"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    outreach_id: Mapped[str] = mapped_column(String(36), ForeignKey("outreach_messages.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    sequence_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False) # 1 for first follow-up, 2 for final
    wait_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    # Statuses: PENDING, DUE, APPROVED, SENT, CANCELLED, CLOSED
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    outreach_message = relationship("OutreachMessage", back_populates="followups")
