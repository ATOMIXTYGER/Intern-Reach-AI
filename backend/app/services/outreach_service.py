from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException, status
from app.models.outreach import OutreachMessage, OutreachEvent
from app.models.contact import Contact, ContactEvidence
from app.models.opportunity import Opportunity
from app.models.candidate import CandidateProfile
from app.models.followup import FollowUp
from app.models.notification import Notification
from app.schemas.outreach import (
    OutreachGenerateRequest,
    OutreachApproveRequest,
    OutreachUpdate,
    LLMMessageResponse,
    DuplicateCheckResult
)
from app.providers.llm.factory import get_llm_provider
from app.utils.prompt_guard import build_secure_prompt, sanitize_external_text
from app.core.logging import logger

BASE_SYSTEM_PROMPT = """You are an expert technical recruiting outreach assistant.
Create a concise and genuine outreach message for a 2028 engineering student.

Rules:
* Never invent facts.
* Never fabricate hiring activity.
* Never fabricate recruiter responsibilities.
* Never claim the recipient reviewed the candidate.
* Never exaggerate candidate experience.
* Mention that the candidate graduates in 2028.
* Mention one genuinely relevant technical connection.
* Keep the message concise.
* Avoid corporate buzzwords.
* Avoid generic flattery.
* Do not immediately demand a referral.
* Ask for guidance when appropriate.
* If asking for a referral, phrase it as an optional request.
* Never pressure the recipient.
* Do not mention AI.

Return JSON adhering strictly to:
{
  "message": "",
  "personalization_reason": "",
  "evidence_used": [],
  "confidence": 0.0
}
"""

async def check_duplicate_outreach(
    db: AsyncSession,
    user_id: str,
    contact_id: str,
    opportunity_id: Optional[str] = None
) -> DuplicateCheckResult:
    """
    Checks for duplicate outreach across contact, company, and opportunity.
    """
    warnings = []
    
    # Get contact details
    c_stmt = select(Contact).where(Contact.id == contact_id)
    c_res = await db.execute(c_stmt)
    contact = c_res.scalar_one_or_none()
    if not contact:
        return DuplicateCheckResult(
            has_contacted_person=False,
            has_contacted_company_recently=False,
            has_contacted_for_opportunity=False,
            warnings=[]
        )

    # 1. Have I contacted this person before?
    prev_person_stmt = select(OutreachMessage).where(
        OutreachMessage.user_id == user_id,
        OutreachMessage.contact_id == contact_id,
        OutreachMessage.status.in_(["APPROVED", "SENT", "REPLIED", "FOLLOW_UP_DUE"])
    )
    person_res = await db.execute(prev_person_stmt)
    has_contacted_person = person_res.scalar_one_or_none() is not None
    if has_contacted_person:
        warnings.append(f"You have already reached out to {contact.name} previously.")

    # 2. Have I contacted another recruiter from the same company recently (within 14 days)?
    two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
    comp_stmt = select(OutreachMessage).join(Contact).where(
        OutreachMessage.user_id == user_id,
        Contact.company_name == contact.company_name,
        OutreachMessage.status.in_(["SENT", "APPROVED"]),
        OutreachMessage.updated_at >= two_weeks_ago
    )
    comp_res = await db.execute(comp_stmt)
    has_contacted_company_recently = comp_res.scalar_one_or_none() is not None
    if has_contacted_company_recently:
        warnings.append(f"You recently reached out to someone at {contact.company_name} within the last 14 days.")

    # 3. Has this person already been contacted for this opportunity?
    has_contacted_for_opportunity = False
    if opportunity_id:
        opp_stmt = select(OutreachMessage).where(
            OutreachMessage.user_id == user_id,
            OutreachMessage.contact_id == contact_id,
            OutreachMessage.opportunity_id == opportunity_id
        )
        opp_res = await db.execute(opp_stmt)
        has_contacted_for_opportunity = opp_res.scalar_one_or_none() is not None
        if has_contacted_for_opportunity:
            warnings.append(f"A message draft or outreach already exists for {contact.name} on this specific opportunity.")

    return DuplicateCheckResult(
        has_contacted_person=has_contacted_person,
        has_contacted_company_recently=has_contacted_company_recently,
        has_contacted_for_opportunity=has_contacted_for_opportunity,
        warnings=warnings
    )

async def generate_outreach_message(
    db: AsyncSession,
    user_id: str,
    req: OutreachGenerateRequest
) -> OutreachMessage:
    # Fetch candidate
    p_stmt = select(CandidateProfile).where(CandidateProfile.user_id == user_id)
    p_res = await db.execute(p_stmt)
    profile = p_res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    # Fetch contact & evidence
    c_stmt = select(Contact).where(Contact.id == req.contact_id)
    c_res = await db.execute(c_stmt)
    contact = c_res.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found.")

    ev_stmt = select(ContactEvidence).where(ContactEvidence.contact_id == contact.id)
    ev_res = await db.execute(ev_stmt)
    evidences = ev_res.scalars().all()
    evidence_text = "\n".join([f"- [{e.source_type}] {e.snippet} ({e.source_url})" for e in evidences]) or "Publicly verified recruiting title."

    # Fetch opportunity if linked
    opportunity = None
    opp_text = "General early career inquiries"
    if req.opportunity_id:
        o_stmt = select(Opportunity).where(Opportunity.id == req.opportunity_id)
        o_res = await db.execute(o_stmt)
        opportunity = o_res.scalar_one_or_none()
        if opportunity:
            opp_text = f"Role: {opportunity.title}\nCompany: {opportunity.company_name}\nLocation: {opportunity.location}\nRequired: {', '.join(opportunity.required_skills)}"

    # Format Candidate Experience
    skills_summary = ", ".join(profile.skills.get("languages", [])[:4] + profile.skills.get("frameworks", [])[:3])
    projects = profile.experiences.get("projects", [])
    project_summary = f"{projects[0].get('title', '')}: {projects[0].get('description', '')}" if projects else "Building scalable fullstack web and AI projects."
    candidate_summary = (
        f"Name: {profile.full_name}\n"
        f"Graduation: {profile.graduation_year} (Target 2028 Graduate)\n"
        f"University: {profile.university or 'Engineering Undergraduate'}\n"
        f"Key Skills: {skills_summary}\n"
        f"Featured Project: {project_summary}"
    )

    contact_summary = (
        f"Name: {contact.name}\n"
        f"Title: {contact.current_title}\n"
        f"Company: {contact.company_name}\n"
        f"Operational Relevance: {contact.operational_relevance} ({contact.relevance_reason})"
    )

    # Strategy adaptation instructions
    strategy_instructions = {
        "RECRUITER": "Goal: Ask about relevant internship opportunities and application guidance for 2028 batch.",
        "HIRING_MANAGER": "Goal: Ask about team technical initiatives, internship opportunities, and recommended application path.",
        "EMPLOYEE": "Goal: Ask for advice about team culture and optionally a referral after establishing relevant background.",
        "EXISTING_CONNECTION": "Goal: Warmer, direct tone referencing mutual alignment and 2028 graduation timeline."
    }.get(req.strategy, "Goal: Ask about internship opportunities and application guidance.")

    # Secure prompt with boundaries
    user_prompt_content = f"""Strategy: {req.strategy}
Channel: {req.channel}
{strategy_instructions}

Candidate:
{candidate_summary}

Opportunity:
{opp_text}

Contact:
{contact_summary}

Verified evidence:
{evidence_text}

Relevant candidate experience:
{project_summary}
"""

    prompt = build_secure_prompt(
        system_instructions=BASE_SYSTEM_PROMPT,
        candidate_data=candidate_summary,
        external_data=f"{opp_text}\n{contact_summary}\n{evidence_text}",
        expected_output_format="JSON object matching LLMMessageResponse schema."
    )

    llm = get_llm_provider()
    try:
        llm_response = await llm.generate_structured(
            system_prompt=BASE_SYSTEM_PROMPT,
            user_prompt=prompt,
            schema_class=LLMMessageResponse,
            temperature=0.25
        )
    except Exception as e:
        logger.error(f"Error generating message via LLM: {e}")
        # Fallback to deterministic message
        llm_response = LLMMessageResponse(
            message=(
                f"Hi {contact.name.split()[0]}, I noticed {contact.company_name}'s technical internship openings. "
                f"As an engineering student graduating in 2028 with background in {skills_summary}, "
                f"I would greatly appreciate any guidance on the application process for undergraduates. Thank you!"
            ),
            personalization_reason="Fallback deterministic outreach referencing 2028 graduation year and candidate skills.",
            evidence_used=["Public company listing"],
            confidence=0.85
        )

    # Save to database in DRAFT status
    outreach = OutreachMessage(
        user_id=user_id,
        opportunity_id=req.opportunity_id,
        contact_id=req.contact_id,
        channel=req.channel,
        strategy=req.strategy,
        subject=f"Inquiry regarding {opportunity.title if opportunity else 'Internship'} - {profile.full_name} (2028 Grad)",
        content=llm_response.message,
        personalization_reason=llm_response.personalization_reason,
        evidence_used=llm_response.evidence_used,
        confidence=llm_response.confidence,
        status="DRAFT",
        message_version=1,
        model_name=llm.provider_name,
        prompt_version="v1.0"
    )
    db.add(outreach)
    await db.flush()

    # Log Outreach Event
    event = OutreachEvent(
        outreach_id=outreach.id,
        event_type="GENERATED",
        details={"strategy": req.strategy, "channel": req.channel, "model": llm.provider_name}
    )
    db.add(event)

    # Create user notification: message awaiting approval
    notif = Notification(
        user_id=user_id,
        notification_type="APPROVAL_AWAITING",
        title="New Outreach Draft Ready",
        message=f"Draft message for {contact.name} at {contact.company_name} is awaiting your approval.",
        link=f"/outreach"
    )
    db.add(notif)

    await db.commit()
    await db.refresh(outreach)
    return outreach

async def approve_outreach_message(
    db: AsyncSession,
    user_id: str,
    outreach_id: str,
    approve_data: OutreachApproveRequest
) -> OutreachMessage:
    stmt = select(OutreachMessage).where(
        OutreachMessage.id == outreach_id,
        OutreachMessage.user_id == user_id
    )
    res = await db.execute(stmt)
    outreach = res.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach message not found.")

    if approve_data.edited_content:
        outreach.content = approve_data.edited_content
        outreach.message_version += 1

    outreach.status = "APPROVED"
    outreach.approved_at = datetime.now(timezone.utc)
    outreach.approved_by = approve_data.approved_by or user_id

    event = OutreachEvent(
        outreach_id=outreach.id,
        event_type="APPROVED",
        details={"approved_by": outreach.approved_by, "version": outreach.message_version}
    )
    db.add(event)
    await db.commit()
    await db.refresh(outreach)
    return outreach

async def mark_outreach_sent(
    db: AsyncSession,
    user_id: str,
    outreach_id: str
) -> OutreachMessage:
    stmt = select(OutreachMessage).where(
        OutreachMessage.id == outreach_id,
        OutreachMessage.user_id == user_id
    )
    res = await db.execute(stmt)
    outreach = res.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach message not found.")

    now = datetime.now(timezone.utc)
    outreach.status = "SENT"
    outreach.sent_at = now
    outreach.last_contacted_at = now

    event = OutreachEvent(
        outreach_id=outreach.id,
        event_type="SENT",
        details={"sent_at": now.isoformat()}
    )
    db.add(event)

    # Section 16: Automatically schedule first follow-up due in 7 days
    due_date = now + timedelta(days=7)
    followup = FollowUp(
        outreach_id=outreach.id,
        user_id=user_id,
        sequence_number=1,
        wait_days=7,
        due_date=due_date,
        status="PENDING",
        content=(
            "Hi, following up on my previous note. Wanted to check if your team is currently "
            "reviewing 2028 undergraduate engineering applications for the internship role. Thanks!"
        )
    )
    db.add(followup)

    await db.commit()
    await db.refresh(outreach)
    return outreach
