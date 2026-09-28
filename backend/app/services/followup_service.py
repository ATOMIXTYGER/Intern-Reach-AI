from typing import List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException
from app.models.followup import FollowUp
from app.models.outreach import OutreachMessage
from app.models.notification import Notification

async def check_and_update_due_followups(db: AsyncSession, user_id: str) -> List[FollowUp]:
    """
    Checks follow-ups that have crossed their due_date and marks them as DUE.
    Creates a notification for the user. Never sends automatically.
    """
    now = datetime.now(timezone.utc)
    stmt = select(FollowUp).where(
        FollowUp.user_id == user_id,
        FollowUp.status == "PENDING",
        FollowUp.due_date <= now
    )
    res = await db.execute(stmt)
    due_items = res.scalars().all()

    for item in due_items:
        item.status = "DUE"
        # Create notification
        notif = Notification(
            user_id=user_id,
            notification_type="FOLLOW_UP_DUE",
            title="Follow-Up Reminder Due",
            message=f"Follow-up #{item.sequence_number} is due for outreach review.",
            link="/followups"
        )
        db.add(notif)

    if due_items:
        await db.commit()
        for item in due_items:
            await db.refresh(item)

    return due_items

async def approve_followup(db: AsyncSession, user_id: str, followup_id: str) -> FollowUp:
    stmt = select(FollowUp).where(FollowUp.id == followup_id, FollowUp.user_id == user_id)
    res = await db.execute(stmt)
    followup = res.scalar_one_or_none()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found.")

    followup.status = "APPROVED"
    followup.approved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(followup)
    return followup

async def mark_followup_sent(db: AsyncSession, user_id: str, followup_id: str) -> FollowUp:
    stmt = select(FollowUp).where(FollowUp.id == followup_id, FollowUp.user_id == user_id)
    res = await db.execute(stmt)
    followup = res.scalar_one_or_none()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found.")

    now = datetime.now(timezone.utc)
    followup.status = "SENT"
    followup.sent_at = now

    # Check if this was sequence 1, schedule final close after 8 days
    if followup.sequence_number == 1:
        # Schedule sequence 2 (final check before close)
        next_followup = FollowUp(
            outreach_id=followup.outreach_id,
            user_id=user_id,
            sequence_number=2,
            wait_days=8,
            due_date=now + timedelta(days=8),
            status="PENDING",
            content="Final check: Close outreach if no response received."
        )
        db.add(next_followup)
    else:
        # Close the parent outreach
        o_stmt = select(OutreachMessage).where(OutreachMessage.id == followup.outreach_id)
        o_res = await db.execute(o_stmt)
        outreach = o_res.scalar_one_or_none()
        if outreach:
            outreach.status = "CLOSED"

    await db.commit()
    await db.refresh(followup)
    return followup
