import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.candidate import CandidateProfile, Resume
from app.schemas.candidate import CandidateProfileUpdate
from app.services.resume_parser import parse_resume_document
from app.core.config import settings

async def get_candidate_profile(db: AsyncSession, user_id: str) -> CandidateProfile:
    stmt = select(CandidateProfile).where(CandidateProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found."
        )
    return profile

async def update_candidate_profile(
    db: AsyncSession,
    user_id: str,
    update_data: CandidateProfileUpdate
) -> CandidateProfile:
    profile = await get_candidate_profile(db, user_id)
    
    # Update fields
    profile.full_name = update_data.full_name
    profile.university = update_data.university
    profile.degree = update_data.degree
    profile.graduation_year = update_data.graduation_year
    profile.current_year = update_data.current_year
    profile.location = update_data.location
    profile.preferred_locations = update_data.preferred_locations
    profile.email = update_data.email
    profile.linkedin_url = update_data.linkedin_url
    profile.github_url = update_data.github_url
    profile.portfolio_url = update_data.portfolio_url

    profile.target_roles = update_data.target_roles
    profile.target_industries = update_data.target_industries
    profile.target_companies = update_data.target_companies
    profile.preferred_company_sizes = update_data.preferred_company_sizes
    profile.preferred_internship_duration = update_data.preferred_internship_duration
    profile.remote_preference = update_data.remote_preference

    profile.skills = update_data.skills.model_dump()
    profile.experiences = update_data.experiences.model_dump()

    await db.commit()
    await db.refresh(profile)
    return profile

async def upload_and_process_resume(
    db: AsyncSession,
    user_id: str,
    filename: str,
    content: bytes,
    mime_type: str
) -> CandidateProfile:
    # 1. Parse safely
    raw_text, structured_data = parse_resume_document(filename, content)

    # 2. Save physical file locally or in storage
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(settings.UPLOAD_DIR, f"{user_id}_{filename}")
    with open(save_path, "wb") as f:
        f.write(content)

    # 3. Create Resume record
    resume_record = Resume(
        user_id=user_id,
        file_name=filename,
        file_size=len(content),
        mime_type=mime_type,
        file_path=save_path,
        extracted_text=raw_text,
        structured_data=structured_data
    )
    db.add(resume_record)

    # 4. Update candidate profile with extracted data without overwriting verified manual edits
    profile = await get_candidate_profile(db, user_id)
    profile.raw_resume_text = raw_text
    profile.structured_resume = structured_data
    
    # Merge newly detected skills if not present
    existing_skills = profile.skills.get("languages", []) + profile.skills.get("frameworks", [])
    new_skills = [s for s in structured_data.get("detected_skills", []) if s not in existing_skills]
    if new_skills:
        # Append to languages or tools
        profile.skills.setdefault("tools", []).extend(new_skills[:5])

    if structured_data.get("graduation_year"):
        profile.graduation_year = structured_data["graduation_year"]
    if structured_data.get("github_url") and not profile.github_url:
        profile.github_url = structured_data["github_url"]
    if structured_data.get("linkedin_url") and not profile.linkedin_url:
        profile.linkedin_url = structured_data["linkedin_url"]

    await db.commit()
    await db.refresh(profile)
    return profile
