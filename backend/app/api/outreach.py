from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.schemas.outreach import (
    OutreachOut,
    OutreachGenerateRequest,
    OutreachApproveRequest,
    OutreachUpdate,
    OutreachStatusUpdate,
    DuplicateCheckResult
)
from app.models.outreach import OutreachMessage
from app.models.contact import Contact
from app.services.outreach_service import (
    generate_outreach_message,
    approve_outreach_message,
    mark_outreach_sent,
    check_duplicate_outreach
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/outreach", tags=["Outreach CRM"])

@router.get("", response_model=List[OutreachOut])
async def list_outreach(
    status: Optional[str] = None,
    channel: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = (
        select(OutreachMessage)
        .options(
            selectinload(OutreachMessage.contact).selectinload(Contact.evidence),
            selectinload(OutreachMessage.opportunity)
        )
        .where(OutreachMessage.user_id == current_user.id)
    )
    if status:
        query = query.where(OutreachMessage.status == status)
    if channel:
        query = query.where(OutreachMessage.channel == channel)

    query = query.order_by(OutreachMessage.updated_at.desc()).limit(limit).offset(offset)
    res = await db.execute(query)
    return res.scalars().all()

@router.get("/duplicate-check", response_model=DuplicateCheckResult)
async def check_duplicates(
    contact_id: str,
    opportunity_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await check_duplicate_outreach(
        db=db,
        user_id=current_user.id,
        contact_id=contact_id,
        opportunity_id=opportunity_id
    )

@router.post("/generate", response_model=OutreachOut)
async def generate_outreach(
    req: OutreachGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    outreach = await generate_outreach_message(db, current_user.id, req)
    # Reload with relationships
    stmt = (
        select(OutreachMessage)
        .options(
            selectinload(OutreachMessage.contact).selectinload(Contact.evidence),
            selectinload(OutreachMessage.opportunity)
        )
        .where(OutreachMessage.id == outreach.id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()

@router.put("/{id}", response_model=OutreachOut)
async def update_outreach(
    id: str,
    update_in: OutreachUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(OutreachMessage).where(OutreachMessage.id == id, OutreachMessage.user_id == current_user.id)
    res = await db.execute(stmt)
    outreach = res.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach message not found.")

    if update_in.content is not None and update_in.content != outreach.content:
        outreach.content = update_in.content
        outreach.message_version += 1
    if update_in.subject is not None:
        outreach.subject = update_in.subject
    if update_in.channel is not None:
        outreach.channel = update_in.channel
    if update_in.strategy is not None:
        outreach.strategy = update_in.strategy
    if update_in.notes is not None:
        outreach.notes = update_in.notes

    await db.commit()
    await db.refresh(outreach)
    return outreach

@router.post("/{id}/approve", response_model=OutreachOut)
async def approve_outreach(
    id: str,
    approve_data: OutreachApproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    outreach = await approve_outreach_message(db, current_user.id, id, approve_data)
    stmt = (
        select(OutreachMessage)
        .options(
            selectinload(OutreachMessage.contact).selectinload(Contact.evidence),
            selectinload(OutreachMessage.opportunity)
        )
        .where(OutreachMessage.id == outreach.id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()

@router.post("/{id}/reject", response_model=OutreachOut)
async def reject_outreach(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(OutreachMessage).where(OutreachMessage.id == id, OutreachMessage.user_id == current_user.id)
    res = await db.execute(stmt)
    outreach = res.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach message not found.")

    outreach.status = "CLOSED"
    await db.commit()
    await db.refresh(outreach)
    return outreach

@router.post("/{id}/sent", response_model=OutreachOut)
async def mark_sent(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    outreach = await mark_outreach_sent(db, current_user.id, id)
    stmt = (
        select(OutreachMessage)
        .options(
            selectinload(OutreachMessage.contact).selectinload(Contact.evidence),
            selectinload(OutreachMessage.opportunity)
        )
        .where(OutreachMessage.id == outreach.id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()

@router.post("/{id}/status", response_model=OutreachOut)
async def update_status(
    id: str,
    status_update: OutreachStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(OutreachMessage).where(OutreachMessage.id == id, OutreachMessage.user_id == current_user.id)
    res = await db.execute(stmt)
    outreach = res.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach message not found.")

    outreach.status = status_update.status
    if status_update.notes:
        outreach.notes = status_update.notes

    await db.commit()
    await db.refresh(outreach)
    return outreach
