from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.candidate import CandidateProfile
from app.models.opportunity import Opportunity
from app.models.match import MatchResult
from app.core.config import settings

def compute_match_scores(
    profile: CandidateProfile,
    opportunity: Opportunity
) -> Dict[str, Any]:
    """
    Computes deterministic match metrics between candidate profile and opportunity.
    Used for internal prioritization.
    """
    opp_text = f"{opportunity.title} {opportunity.job_description}".lower()
    
    # 1. Skill Match
    candidate_skills = set()
    for cat, sk_list in profile.skills.items():
        if isinstance(sk_list, list):
            for s in sk_list:
                candidate_skills.add(s.strip())

    req_skills = set(opportunity.required_skills)
    pref_skills = set(opportunity.preferred_skills)
    all_opp_skills = req_skills.union(pref_skills)

    # If no explicit list in opportunity, search for candidate skills in JD text
    if not all_opp_skills:
        for skill in candidate_skills:
            if skill.lower() in opp_text:
                all_opp_skills.add(skill)

    matched_skills = [s for s in all_opp_skills if any(cs.lower() == s.lower() for cs in candidate_skills)]
    missing_skills = [s for s in req_skills if not any(cs.lower() == s.lower() for cs in candidate_skills)]

    if all_opp_skills:
        skill_score = min(100.0, (len(matched_skills) / len(all_opp_skills)) * 100.0)
    else:
        skill_score = 75.0

    # 2. Role Match
    target_roles = profile.target_roles or []
    role_match = 0.0
    for r in target_roles:
        if any(token in opportunity.title.lower() for token in r.lower().split()):
            role_match = 95.0
            break
    if role_match == 0.0:
        role_match = 70.0 if "intern" in opportunity.title.lower() else 50.0

    # 3. Eligibility Match (Target: 2028 Graduate)
    eligibility_match = 90.0
    eligibility_reasons = []
    concerns = []

    if opportunity.eligibility_status == "eligible":
        eligibility_match = 95.0
        eligibility_reasons.append(f"Confirmed eligibility for {profile.graduation_year} graduation cycle.")
    elif opportunity.eligibility_status == "possibly_eligible":
        eligibility_match = 75.0
        eligibility_reasons.append(f"Potentially open to {profile.graduation_year} students; requires direct recruiter inquiry.")
    elif opportunity.eligibility_status == "not_eligible":
        eligibility_match = 30.0
        concerns.append("Listing requirements may not match sophomore graduation cohort.")
    else:
        eligibility_reasons.append(f"Graduation eligibility unconfirmed in public posting; outreach needed.")

    # 4. Location Match
    loc_score = 50.0
    pref_locs = profile.preferred_locations or []
    if "remote" in opportunity.location.lower():
        loc_score = 100.0
    else:
        for pl in pref_locs:
            if pl.lower() in opportunity.location.lower():
                loc_score = 95.0
                break
            elif "india" in pl.lower() and "india" in opportunity.location.lower():
                loc_score = 85.0

    # 5. Experience / Project Match
    relevant_projects = []
    projects = profile.experiences.get("projects", [])
    for p in projects:
        techs = p.get("technologies", [])
        if any(t.lower() in opp_text for t in techs) or any(t in matched_skills for t in techs):
            relevant_projects.append(p.get("title", "Technical Project"))

    experience_score = 80.0 if relevant_projects else 65.0

    # Weighted Overall Prioritization Score
    overall = (
        (skill_score * 0.35) +
        (role_match * 0.25) +
        (eligibility_match * 0.20) +
        (location_score_weight := loc_score * 0.10) +
        (experience_score * 0.10)
    )

    return {
        "overall_match_score": round(overall, 1),
        "role_match": round(role_match, 1),
        "skill_match": round(skill_score, 1),
        "eligibility_match": round(eligibility_match, 1),
        "location_match": round(loc_score, 1),
        "experience_match": round(experience_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "relevant_projects": relevant_projects[:3],
        "eligibility_reasoning": eligibility_reasons,
        "concerns": concerns,
        "model_name": "deterministic_matcher_v1",
        "prompt_version": "v1.0"
    }

async def create_or_update_match(
    db: AsyncSession,
    user_id: str,
    opportunity_id: str
) -> MatchResult:
    # Fetch profile and opportunity
    p_stmt = select(CandidateProfile).where(CandidateProfile.user_id == user_id)
    p_res = await db.execute(p_stmt)
    profile = p_res.scalar_one_or_none()

    o_stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    o_res = await db.execute(o_stmt)
    opportunity = o_res.scalar_one_or_none()

    if not profile or not opportunity:
        raise ValueError("Profile or Opportunity not found.")

    scores = compute_match_scores(profile, opportunity)

    # Check existing match
    m_stmt = select(MatchResult).where(
        MatchResult.user_id == user_id,
        MatchResult.opportunity_id == opportunity_id
    )
    m_res = await db.execute(m_stmt)
    match_record = m_res.scalar_one_or_none()

    if not match_record:
        match_record = MatchResult(
            user_id=user_id,
            opportunity_id=opportunity_id,
            **scores
        )
        db.add(match_record)
    else:
        for k, v in scores.items():
            setattr(match_record, k, v)

    await db.commit()
    await db.refresh(match_record)
    return match_record
