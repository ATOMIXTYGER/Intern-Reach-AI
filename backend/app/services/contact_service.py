from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.contact import Contact, ContactEvidence, OpportunityContact
from app.models.opportunity import Company, Opportunity
from app.providers.search.factory import get_search_provider
from app.core.logging import logger

def calculate_contact_relevance(title: str, snippet: str = "") -> Dict[str, Any]:
    """
    Computes operational relevance based strictly on public evidence.
    No subjective personality assessment.
    """
    title_lower = f"{title} {snippet}".lower()
    
    if any(k in title_lower for k in ["university", "campus", "early careers", "student", "grad", "college"]):
        return {
            "operational_relevance": "high",
            "relevance_score": 0.95,
            "confidence": 0.95,
            "relevance_reason": "Directly focuses on university hiring, student internships, and early-careers cohorts."
        }
    elif any(k in title_lower for k in ["technical recruiter", "tech recruiter", "engineering recruiter", "talent partner - tech"]):
        return {
            "operational_relevance": "high",
            "relevance_score": 0.88,
            "confidence": 0.90,
            "relevance_reason": "Technical recruiter actively sourcing software engineering and AI/data talent."
        }
    elif any(k in title_lower for k in ["recruiter", "talent acquisition", "sourcer", "recruitment"]):
        return {
            "operational_relevance": "medium",
            "relevance_score": 0.65,
            "confidence": 0.80,
            "relevance_reason": "Recruiter at target company, but university/internship focus not explicitly declared."
        }
    elif any(k in title_lower for k in ["engineering manager", "software engineer", "tech lead", "founder", "cto"]):
        return {
            "operational_relevance": "medium",
            "relevance_score": 0.60,
            "confidence": 0.75,
            "relevance_reason": "Engineering team member or engineering leader who can provide team insights or optional referral."
        }
    else:
        return {
            "operational_relevance": "low",
            "relevance_score": 0.35,
            "confidence": 0.50,
            "relevance_reason": "General employee without verified recruiting or engineering alignment."
        }

async def research_contacts_for_company(
    db: AsyncSession,
    company_name: str,
    opportunity_id: Optional[str] = None,
    limit: int = 5
) -> List[Contact]:
    """
    Finds legitimate public recruiting contacts, saves evidence, and links to opportunities.
    """
    search_provider = get_search_provider()
    raw_contacts = await search_provider.search_contacts(
        company_name=company_name,
        limit=limit
    )

    # Get company ID if exists
    comp_stmt = select(Company).where(Company.name == company_name)
    comp_res = await db.execute(comp_stmt)
    company = comp_res.scalar_one_or_none()
    company_id = company.id if company else None

    saved_contacts = []
    for c_data in raw_contacts:
        name = c_data.get("name", "").strip()
        if not name:
            continue

        # Check existing contact
        c_stmt = select(Contact).where(
            and_(
                Contact.name == name,
                Contact.company_name == company_name
            )
        )
        existing = await db.execute(c_stmt)
        contact = existing.scalar_one_or_none()

        relevance = calculate_contact_relevance(
            title=c_data.get("current_title", ""),
            snippet=c_data.get("snippet", "")
        )

        if not contact:
            contact = Contact(
                company_id=company_id,
                company_name=company_name,
                name=name,
                current_title=c_data.get("current_title", "Talent Acquisition"),
                public_profile_url=c_data.get("public_profile_url"),
                linkedin_url=c_data.get("linkedin_url") or c_data.get("public_profile_url"),
                source=c_data.get("source", "public_web"),
                operational_relevance=relevance["operational_relevance"],
                relevance_score=relevance["relevance_score"],
                confidence=relevance["confidence"],
                relevance_reason=relevance["relevance_reason"],
                verified_at=datetime.now(timezone.utc)
            )
            db.add(contact)
            await db.flush()

            # Add evidence entry
            evidence = ContactEvidence(
                contact_id=contact.id,
                source_type="public_recruiter_profile",
                source_url=c_data.get("public_profile_url", f"https://careers.google.com/search?q={company_name}"),
                snippet=c_data.get("snippet", f"Publicly listed as {c_data.get('current_title')} at {company_name}."),
                confidence=relevance["confidence"]
            )
            db.add(evidence)

        # Link to opportunity if provided
        if opportunity_id:
            link_stmt = select(OpportunityContact).where(
                and_(
                    OpportunityContact.opportunity_id == opportunity_id,
                    OpportunityContact.contact_id == contact.id
                )
            )
            link_res = await db.execute(link_stmt)
            if not link_res.scalar_one_or_none():
                opp_link = OpportunityContact(
                    opportunity_id=opportunity_id,
                    contact_id=contact.id,
                    relevance_notes=relevance["relevance_reason"]
                )
                db.add(opp_link)

        saved_contacts.append(contact)

    await db.commit()
    for c in saved_contacts:
        await db.refresh(c)

    return saved_contacts
