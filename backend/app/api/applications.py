from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.application import ApplicationOut, ApplicationCreate, ApplicationUpdate
from app.services.application_service import (
    list_applications,
    create_application,
    update_application
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/applications", tags=["Application Tracker"])

@router.get("", response_model=List[ApplicationOut])
async def get_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await list_applications(db, current_user.id)

@router.post("", response_model=ApplicationOut)
async def add_application(
    app_in: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_application(db, current_user.id, app_in)

@router.put("/{id}", response_model=ApplicationOut)
async def modify_application(
    id: str,
    app_in: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_application(db, current_user.id, id, app_in)
