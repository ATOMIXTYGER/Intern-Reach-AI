from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc
from app.db.session import get_db
from app.schemas.opportunity import (
    OpportunityOut,
    OpportunitySearchRequest,
    VerificationResult
)
from app.models.opportunity import Opportunity
from app.models.match import MatchResult
from app.services.opportunity_service import discover_opportunities, verify_opportunity_with_agent
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

@router.get("", response_model=List[OpportunityOut])
async def list_opportunities(
    company: Optional[str] = None,
    location: Optional[str] = None,
    role: Optional[str] = None,
    eligibility: Optional[str] = None,
    source: Optional[str] = None,
    sort_by: str = Query("newest", pattern="^(newest|deadline|company)$"),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Opportunity).where(Opportunity.is_active == True)

    if company:
        query = query.where(Opportunity.company_name.ilike(f"%{company}%"))
    if location:
        query = query.where(Opportunity.location.ilike(f"%{location}%"))
    if role:
        query = query.where(Opportunity.title.ilike(f"%{role}%"))
    if eligibility:
        query = query.where(Opportunity.eligibility_status == eligibility)
    if source:
        query = query.where(Opportunity.source == source)

    if sort_by == "deadline":
        query = query.order_by(Opportunity.deadline.asc().nulls_last())
    elif sort_by == "company":
        query = query.order_by(Opportunity.company_name.asc())
    else:
        query = query.order_by(Opportunity.date_discovered.desc())

    query = query.limit(limit).offset(offset)
    res = await db.execute(query)
    return res.scalars().all()

@router.get("/{id}", response_model=OpportunityOut)
async def get_opportunity(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Opportunity).where(Opportunity.id == id)
    res = await db.execute(stmt)
    opp = res.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    return opp

@router.post("/search", response_model=List[OpportunityOut])
async def search_opportunities_endpoint(
    search_params: OpportunitySearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes Opportunity Discovery Agent to discover and verify new internships.
    """
    discovered = await discover_opportunities(
        db=db,
        search_params=search_params,
        limit=10
    )
    return discovered

@router.post("/{id}/verify", response_model=VerificationResult)
async def verify_opportunity_endpoint(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Opportunity).where(Opportunity.id == id)
    res = await db.execute(stmt)
    opp = res.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")

    ver_res = await verify_opportunity_with_agent(opp, candidate_grad_year=2028)
    
    # Update stored verification result
    opp.verified = ver_res.verified
    opp.eligibility_status = ver_res.eligibility
    opp.verification_confidence = ver_res.confidence
    opp.verification_reasons = ver_res.reasons
    await db.commit()
    await db.refresh(opp)

    return ver_res
