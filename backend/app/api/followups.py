from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.schemas.followup import FollowUpOut, FollowUpUpdate
from app.models.followup import FollowUp
from app.services.followup_service import (
    check_and_update_due_followups,
    approve_followup,
    mark_followup_sent
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/followups", tags=["Follow-ups"])

@router.get("", response_model=List[FollowUpOut])
async def list_followups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Automatically scan for due items
    await check_and_update_due_followups(db, current_user.id)
    
    stmt = select(FollowUp).where(FollowUp.user_id == current_user.id).order_by(FollowUp.due_date.asc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.put("/{id}", response_model=FollowUpOut)
async def update_followup_content(
    id: str,
    update_in: FollowUpUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(FollowUp).where(FollowUp.id == id, FollowUp.user_id == current_user.id)
    res = await db.execute(stmt)
    followup = res.scalar_one_or_none()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found.")

    if update_in.content is not None:
        followup.content = update_in.content
    if update_in.notes is not None:
        followup.notes = update_in.notes
    if update_in.status is not None:
        followup.status = update_in.status
    if update_in.due_date is not None:
        followup.due_date = update_in.due_date

    await db.commit()
    await db.refresh(followup)
    return followup

@router.post("/{id}/approve", response_model=FollowUpOut)
async def approve_followup_endpoint(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await approve_followup(db, current_user.id, id)

@router.post("/{id}/sent", response_model=FollowUpOut)
async def mark_followup_sent_endpoint(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await mark_followup_sent(db, current_user.id, id)
