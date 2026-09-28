from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.candidate import CandidateProfileOut, CandidateProfileUpdate
from app.services.candidate_service import (
    get_candidate_profile,
    update_candidate_profile,
    upload_and_process_resume
)
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/candidate", tags=["Candidate Profile"])

@router.get("", response_model=CandidateProfileOut)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = await get_candidate_profile(db, current_user.id)
    return profile

@router.put("", response_model=CandidateProfileOut)
async def update_profile(
    update_in: CandidateProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = await update_candidate_profile(db, current_user.id, update_in)
    return profile

@router.post("/resume", response_model=CandidateProfileOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ("pdf", "docx", "doc"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported format. Please upload a PDF or DOCX resume."
        )

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum 10MB limit."
        )

    try:
        profile = await upload_and_process_resume(
            db=db,
            user_id=current_user.id,
            filename=file.filename,
            content=content,
            mime_type=file.content_type or "application/octet-stream"
        )
        return profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
