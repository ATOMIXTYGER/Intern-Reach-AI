from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.schemas.contact import ContactOut, ContactResearchRequest
from app.models.contact import Contact
from app.services.contact_service import research_contacts_for_company
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.get("", response_model=List[ContactOut])
async def list_contacts(
    company: Optional[str] = None,
    relevance: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Contact).options(selectinload(Contact.evidence))
    if company:
        query = query.where(Contact.company_name.ilike(f"%{company}%"))
    if relevance:
        query = query.where(Contact.operational_relevance == relevance)

    query = query.order_by(Contact.relevance_score.desc()).limit(limit).offset(offset)
    res = await db.execute(query)
    return res.scalars().all()

@router.get("/{id}", response_model=ContactOut)
async def get_contact(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Contact).options(selectinload(Contact.evidence)).where(Contact.id == id)
    res = await db.execute(stmt)
    contact = res.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found.")
    return contact

@router.post("/research", response_model=List[ContactOut])
async def research_contacts_endpoint(
    req: ContactResearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes Contact Research Agent to locate verified public recruiting contacts.
    """
    contacts = await research_contacts_for_company(
        db=db,
        company_name=req.company_name,
        opportunity_id=req.opportunity_id,
        limit=5
    )
    # Reload with evidence
    reloaded = []
    for c in contacts:
        stmt = select(Contact).options(selectinload(Contact.evidence)).where(Contact.id == c.id)
        res = await db.execute(stmt)
        reloaded.append(res.scalar_one())
    return reloaded
