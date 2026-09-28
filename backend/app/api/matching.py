from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.schemas.match import MatchResultOut
from app.models.match import MatchResult
from app.services.matching_service import create_or_update_match
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/matches", tags=["Matching"])

@router.post("/{opportunity_id}", response_model=MatchResultOut)
async def run_match_for_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        match_result = await create_or_update_match(
            db=db,
            user_id=current_user.id,
            opportunity_id=opportunity_id
        )
        return match_result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{opportunity_id}", response_model=MatchResultOut)
async def get_match_for_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(MatchResult).where(
        MatchResult.user_id == current_user.id,
        MatchResult.opportunity_id == opportunity_id
    )
    res = await db.execute(stmt)
    match_result = res.scalar_one_or_none()
    if not match_result:
        # Generate on demand
        try:
            match_result = await create_or_update_match(
                db=db,
                user_id=current_user.id,
                opportunity_id=opportunity_id
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    return match_result
