from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate

async def list_applications(db: AsyncSession, user_id: str) -> List[Application]:
    stmt = select(Application).where(Application.user_id == user_id).order_by(Application.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

async def create_application(db: AsyncSession, user_id: str, app_in: ApplicationCreate) -> Application:
    app_record = Application(
        user_id=user_id,
        opportunity_id=app_in.opportunity_id,
        company_name=app_in.company_name,
        role_title=app_in.role_title,
        application_url=app_in.application_url,
        date_applied=app_in.date_applied or datetime.now(timezone.utc),
        status=app_in.status,
        referral_contact_id=app_in.referral_contact_id,
        recruiter_contact_id=app_in.recruiter_contact_id,
        interview_stage=app_in.interview_stage,
        next_action=app_in.next_action,
        deadline=app_in.deadline,
        notes=app_in.notes
    )
    db.add(app_record)
    await db.commit()
    await db.refresh(app_record)
    return app_record

async def update_application(
    db: AsyncSession,
    user_id: str,
    application_id: str,
    app_in: ApplicationUpdate
) -> Application:
    stmt = select(Application).where(Application.id == application_id, Application.user_id == user_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Application not found.")

    for field, value in app_in.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)
    return record
