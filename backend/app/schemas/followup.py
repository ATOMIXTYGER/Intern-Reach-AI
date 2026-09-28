from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FollowUpGenerateRequest(BaseModel):
    outreach_id: str
    custom_instructions: Optional[str] = None

class FollowUpUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    due_date: Optional[datetime] = None

class FollowUpOut(BaseModel):
    id: str
    outreach_id: str
    user_id: str
    sequence_number: int
    wait_days: int
    due_date: datetime
    status: str # PENDING, DUE, APPROVED, SENT, CANCELLED, CLOSED
    content: Optional[str] = None
    notes: Optional[str] = None
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
