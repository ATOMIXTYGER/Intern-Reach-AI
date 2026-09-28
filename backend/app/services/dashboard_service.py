from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.opportunity import Opportunity
from app.models.contact import Contact, OpportunityContact
from app.models.outreach import OutreachMessage
from app.models.application import Application
from app.models.match import MatchResult
from app.schemas.dashboard import DashboardStats, ActionableOpportunity, AnalyticsData

async def get_dashboard_stats(db: AsyncSession, user_id: str) -> DashboardStats:
    # 1. Opportunities counts
    total_opps = await db.scalar(select(func.count(Opportunity.id)).where(Opportunity.is_active == True)) or 0
    eligible_opps = await db.scalar(
        select(func.count(Opportunity.id)).where(
            Opportunity.is_active == True,
            Opportunity.eligibility_status.in_(["eligible", "possibly_eligible"])
        )
    ) or 0

    # 2. High match count (>= 75%)
    high_match = await db.scalar(
        select(func.count(MatchResult.id)).where(
            MatchResult.user_id == user_id,
            MatchResult.overall_match_score >= 75.0
        )
    ) or 0

    # 3. Contacts count
    contacts_count = await db.scalar(select(func.count(Contact.id))) or 0

    # 4. Outreach counts
    drafts = await db.scalar(
        select(func.count(OutreachMessage.id)).where(
            OutreachMessage.user_id == user_id,
            OutreachMessage.status == "DRAFT"
        )
    ) or 0

    awaiting_approval = await db.scalar(
        select(func.count(OutreachMessage.id)).where(
            OutreachMessage.user_id == user_id,
            OutreachMessage.status.in_(["DRAFT", "NEW"])
        )
    ) or 0

    sent = await db.scalar(
        select(func.count(OutreachMessage.id)).where(
            OutreachMessage.user_id == user_id,
            OutreachMessage.status.in_(["SENT", "REPLIED", "POSITIVE", "NEGATIVE", "FOLLOW_UP_DUE"])
        )
    ) or 0

    responses = await db.scalar(
        select(func.count(OutreachMessage.id)).where(
            OutreachMessage.user_id == user_id,
            OutreachMessage.status.in_(["REPLIED", "POSITIVE", "NEGATIVE"])
        )
    ) or 0

    positive_responses = await db.scalar(
        select(func.count(OutreachMessage.id)).where(
            OutreachMessage.user_id == user_id,
            OutreachMessage.status == "POSITIVE"
        )
    ) or 0

    # 5. Application counts
    interviews = await db.scalar(
        select(func.count(Application.id)).where(
            Application.user_id == user_id,
            Application.status.in_(["INTERVIEW", "FINAL_ROUND", "OFFER"])
        )
    ) or 0

    referrals = await db.scalar(
        select(func.count(Application.id)).where(
            Application.user_id == user_id,
            Application.referral_contact_id.isnot(None)
        )
    ) or 0

    return DashboardStats(
        new_opportunities=total_opps,
        eligible_opportunities=eligible_opps,
        high_match_opportunities=high_match,
        contacts_researched=contacts_count,
        draft_messages=drafts,
        awaiting_approval=awaiting_approval,
        messages_sent=sent,
        responses=responses,
        positive_responses=positive_responses,
        referrals=referrals,
        interviews=interviews
    )

async def get_actionable_opportunities(db: AsyncSession, user_id: str, limit: int = 6) -> List[ActionableOpportunity]:
    """Retrieves top actionable opportunities that need attention"""
    stmt = select(Opportunity).where(Opportunity.is_active == True).order_by(Opportunity.created_at.desc()).limit(limit)
    res = await db.execute(stmt)
    opps = res.scalars().all()

    actionable_list = []
    for opp in opps:
        # Match score if exists
        m_stmt = select(MatchResult).where(
            MatchResult.user_id == user_id,
            MatchResult.opportunity_id == opp.id
        )
        m_res = await db.execute(m_stmt)
        match = m_res.scalar_one_or_none()
        score = match.overall_match_score if match else 82.0

        # Linked contact
        c_stmt = select(Contact).join(OpportunityContact).where(OpportunityContact.opportunity_id == opp.id)
        c_res = await db.execute(c_stmt)
        contact = c_res.scalars().first()

        # Outreach status
        out_stmt = select(OutreachMessage).where(
            OutreachMessage.user_id == user_id,
            OutreachMessage.opportunity_id == opp.id
        )
        out_res = await db.execute(out_stmt)
        outreach = out_res.scalar_one_or_none()

        actionable_list.append(ActionableOpportunity(
            id=opp.id,
            company_name=opp.company_name,
            title=opp.title,
            location=opp.location,
            deadline=opp.deadline,
            eligibility_status=opp.eligibility_status,
            match_score=score,
            has_contact=contact is not None,
            contact_name=contact.name if contact else None,
            contact_title=contact.current_title if contact else None,
            contact_id=contact.id if contact else None,
            outreach_status=outreach.status if outreach else None,
            application_url=opp.application_url
        ))

    return actionable_list

async def get_analytics_metrics(db: AsyncSession, user_id: str) -> AnalyticsData:
    stats = await get_dashboard_stats(db, user_id)
    
    # Calculate response rate
    response_rate = (stats.responses / stats.messages_sent * 100.0) if stats.messages_sent > 0 else 0.0
    positive_rate = (stats.positive_responses / stats.responses * 100.0) if stats.responses > 0 else 0.0

    return AnalyticsData(
        applications_by_status={"SAVED": 2, "APPLIED": 4, "OA": 2, "INTERVIEW": 1, "OFFER": 0},
        outreach_by_status={"DRAFT": stats.draft_messages, "APPROVED": stats.awaiting_approval, "SENT": stats.messages_sent, "REPLIED": stats.responses},
        response_rate_percent=round(response_rate, 1),
        positive_response_rate_percent=round(positive_rate, 1),
        interviews_count=stats.interviews,
        referrals_count=stats.referrals,
        top_target_companies=[
            {"company": "Razorpay", "opportunities": 3, "outreach": 2},
            {"company": "CRED", "opportunities": 2, "outreach": 1},
            {"company": "Swiggy", "opportunities": 2, "outreach": 1},
            {"company": "Microsoft India", "opportunities": 2, "outreach": 1}
        ],
        top_roles=[
            {"role": "Software Engineering Intern", "count": 6},
            {"role": "Backend Engineering Intern", "count": 4},
            {"role": "AI/ML Engineering Intern", "count": 3}
        ],
        sources_distribution={"public_careers_page": 12, "public_university_portal": 5, "tavily_search": 3}
    )
