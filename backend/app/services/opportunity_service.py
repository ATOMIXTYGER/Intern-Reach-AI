from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.opportunity import Opportunity, Company
from app.providers.search.factory import get_search_provider
from app.providers.llm.factory import get_llm_provider
from app.schemas.opportunity import VerificationResult, OpportunitySearchRequest
from app.utils.prompt_guard import build_secure_prompt, sanitize_external_text
from app.core.logging import logger

def deterministic_verify_opportunity(
    title: str,
    job_description: str,
    candidate_grad_year: int = 2028,
    target_locations: List[str] = None
) -> VerificationResult:
    """
    Fast, deterministic rule-based verification check before or alongside LLM reasoning.
    Section 29: Use deterministic code for basic rules to save LLM cost.
    """
    reasons = []
    evidence = []
    confidence = 0.85
    
    text_lower = f"{title} {job_description}".lower()
    
    # 1. Is it an internship?
    is_intern = any(term in text_lower for term in ["intern", "internship", "trainee", "student"])
    if not is_intern:
        return VerificationResult(
            verified=False,
            eligibility="not_eligible",
            confidence=0.9,
            reasons=["Position does not appear to be an internship or trainee role."],
            evidence=["Title or JD does not contain internship terms."]
        )
    reasons.append("Role confirmed as an internship/early-careers position.")
    evidence.append("Contains explicit internship keyword in title/description.")

    # 2. Is it technical?
    is_tech = any(term in text_lower for term in [
        "software", "sde", "engineer", "developer", "backend", "frontend",
        "full stack", "fullstack", "ai", "ml", "machine learning", "data", "cloud"
    ])
    if not is_tech:
        return VerificationResult(
            verified=True,
            eligibility="not_eligible",
            confidence=0.85,
            reasons=["Role is an internship, but does not appear to be technical/engineering related."],
            evidence=["Lacks software, engineering, or data keywords."]
        )
    reasons.append("Technical software/engineering domain confirmed.")

    # 3. Graduation eligibility
    eligibility = "eligible"
    if "2024" in text_lower or "2025" in text_lower:
        if "2028" not in text_lower and "undergraduate" not in text_lower and "bachelor" not in text_lower:
            eligibility = "possibly_eligible"
            reasons.append("Listing mentions earlier batch years, but undergraduates may still apply.")
            confidence = 0.70
    
    if str(candidate_grad_year) in text_lower or "2027 or 2028" in text_lower or "undergraduate" in text_lower:
        eligibility = "eligible"
        reasons.append(f"Explicitly open to {candidate_grad_year} graduates or undergraduates.")
        evidence.append(f"Graduation requirement text matches candidate's {candidate_grad_year} timeline.")

    # 4. Location compatibility
    if target_locations:
        loc_match = any(loc.lower() in text_lower for loc in target_locations) or "remote" in text_lower
        if loc_match:
            reasons.append("Location matches candidate's target geography or offers remote work.")
        else:
            reasons.append("Location may require relocation or confirmation.")

    return VerificationResult(
        verified=True,
        eligibility=eligibility,
        confidence=confidence,
        reasons=reasons,
        evidence=evidence
    )

async def verify_opportunity_with_agent(
    opp: Opportunity,
    candidate_grad_year: int = 2028
) -> VerificationResult:
    """Verifies opportunity with LLM agent when deterministic confidence is borderline"""
    base_result = deterministic_verify_opportunity(
        opp.title,
        opp.job_description,
        candidate_grad_year
    )
    if base_result.confidence >= 0.85:
        return base_result

    # Invoke LLM Provider with prompt injection defense
    llm = get_llm_provider()
    system_instructions = (
        "You are an expert technical recruiting verification agent. "
        "Analyze whether this opportunity is a genuine software/AI internship and if a student "
        f"graduating in {candidate_grad_year} appears eligible. "
        "Return strictly the JSON object adhering to the schema."
    )
    prompt = build_secure_prompt(
        system_instructions=system_instructions,
        candidate_data=f"Target Graduation Year: {candidate_grad_year}",
        external_data=f"Title: {opp.title}\nCompany: {opp.company_name}\nDescription: {opp.job_description[:2000]}",
        expected_output_format="JSON adhering to VerificationResult: {verified: bool, eligibility: str, confidence: float, reasons: [], evidence: []}"
    )

    try:
        res = await llm.generate_structured(
            system_prompt=system_instructions,
            user_prompt=prompt,
            schema_class=VerificationResult
        )
        return res
    except Exception as e:
        logger.warning(f"LLM verification failed, falling back to deterministic result: {e}")
        return base_result

async def discover_opportunities(
    db: AsyncSession,
    search_params: OpportunitySearchRequest,
    limit: int = 10
) -> List[Opportunity]:
    """
    Discovers, deduplicates, verifies, and stores opportunities.
    """
    search_provider = get_search_provider()
    raw_results = await search_provider.search_opportunities(
        roles=search_params.target_roles or ["Software Engineering Intern"],
        locations=search_params.locations or ["Bengaluru", "Remote"],
        companies=search_params.target_companies,
        keywords=search_params.keywords,
        limit=limit
    )

    created_opps = []
    for item in raw_results:
        app_url = item.get("application_url", "").strip()
        comp_name = item.get("company_name", "Unknown").strip()
        title = item.get("title", "").strip()

        # Deduplication check by application_url or (company_name + title)
        stmt = select(Opportunity).where(
            or_(
                Opportunity.application_url == app_url,
                and_(
                    Opportunity.company_name == comp_name,
                    Opportunity.title == title
                )
            )
        )
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            continue # Skip duplicate

        # Get or create company
        comp_stmt = select(Company).where(Company.name == comp_name)
        comp_res = await db.execute(comp_stmt)
        company = comp_res.scalar_one_or_none()
        if not company:
            company = Company(
                name=comp_name,
                industry="Technology",
                careers_url=app_url
            )
            db.add(company)
            await db.flush()

        # Verification check
        ver_res = deterministic_verify_opportunity(
            title=title,
            job_description=item.get("job_description", ""),
            candidate_grad_year=search_params.graduation_year or 2028,
            target_locations=search_params.locations
        )

        opp = Opportunity(
            company_id=company.id,
            company_name=comp_name,
            title=title,
            job_description=item.get("job_description", ""),
            location=item.get("location", "India / Remote"),
            internship_duration=item.get("internship_duration"),
            application_url=app_url,
            source=item.get("source", "public_web"),
            date_discovered=datetime.now(timezone.utc),
            graduation_eligibility=item.get("graduation_eligibility"),
            required_skills=item.get("required_skills", []),
            preferred_skills=item.get("preferred_skills", []),
            employment_type=item.get("employment_type", "Internship"),
            evidence_url=item.get("evidence_url", app_url),
            verified=ver_res.verified,
            eligibility_status=ver_res.eligibility,
            verification_confidence=ver_res.confidence,
            verification_reasons=ver_res.reasons,
            is_active=True
        )
        db.add(opp)
        created_opps.append(opp)

    await db.commit()
    for opp in created_opps:
        await db.refresh(opp)

    return created_opps
