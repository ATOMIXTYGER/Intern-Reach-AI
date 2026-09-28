from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from app.models.candidate import CandidateProfile
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email.lower().strip())
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
    
    hashed = get_password_hash(user_in.password)
    user = User(
        email=user_in.email.lower().strip(),
        hashed_password=hashed,
        full_name=user_in.full_name.strip()
    )
    db.add(user)
    await db.flush()

    # Automatically create default candidate profile for 2028 graduate
    profile = CandidateProfile(
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        graduation_year=2028,
        current_year="Sophomore / 2nd Year",
        preferred_locations=["India", "Bengaluru", "Hyderabad", "Pune", "Delhi NCR", "Mumbai", "Remote"],
        target_roles=[
            "Software Engineering Intern",
            "SDE Intern",
            "Backend Engineering Intern",
            "Full Stack Engineering Intern",
            "AI/ML Engineering Intern",
            "Data Engineering Intern"
        ],
        target_industries=["Technology", "Fintech", "AI/ML", "E-commerce"],
        target_companies=["Razorpay", "CRED", "Swiggy", "Microsoft", "Postman", "Zomato"],
        skills={
            "languages": ["Python", "JavaScript", "TypeScript", "SQL", "C++"],
            "frameworks": ["FastAPI", "Next.js", "React", "Node.js"],
            "databases": ["PostgreSQL", "Redis", "SQLite"],
            "cloud": ["AWS", "Docker"],
            "ai_ml": ["PyTorch", "LangChain", "OpenAI/Claude APIs", "Transformers"],
            "tools": ["Git", "GitHub", "Linux", "Postman"]
        },
        experiences={
            "internships": [],
            "projects": [
                {
                    "title": "Distributed Task Queue & API Engine",
                    "description": "Built high-throughput async task queue using FastAPI, Redis, and PostgreSQL with rate-limiting and worker pools.",
                    "technologies": ["FastAPI", "Redis", "PostgreSQL", "Docker"]
                },
                {
                    "title": "LLM Semantic Search & Document Agent",
                    "description": "Implemented RAG pipeline and vector search using LangChain and embeddings for developer documentation.",
                    "technologies": ["Python", "LangChain", "Vector DB", "FastAPI"]
                }
            ],
            "research": [],
            "achievements": ["Finalist at University Hackathon 2024", "Top 5% in Competitive Programming Contest"],
            "leadership": ["Core Technical Member, University Coding Club"],
            "certifications": []
        }
    )
    db.add(profile)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    user_id = decode_access_token(token)
    if not user_id:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exception
    return user
