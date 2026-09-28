from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.schemas.dashboard import DashboardStats, ActionableOpportunity, AnalyticsData
from app.models.notification import Notification
from app.services.dashboard_service import (
    get_dashboard_stats,
    get_actionable_opportunities,
    get_analytics_metrics
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.get("/stats", response_model=DashboardStats)
async def dashboard_stats_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_dashboard_stats(db, current_user.id)

@router.get("/actionable", response_model=List[ActionableOpportunity])
async def actionable_opportunities_endpoint(
    limit: int = 8,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_actionable_opportunities(db, current_user.id, limit=limit)

@router.get("/analytics", response_model=AnalyticsData)
async def analytics_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_analytics_metrics(db, current_user.id)

@router.get("/notifications")
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(20)
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.put("/notifications/{id}/read")
async def mark_notification_read(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Notification).where(Notification.id == id, Notification.user_id == current_user.id)
    res = await db.execute(stmt)
    notif = res.scalar_one_or_none()
    if notif:
        notif.is_read = True
        await db.commit()
    return {"status": "success"}
