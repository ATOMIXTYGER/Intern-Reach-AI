from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.db.base import Base

connect_args = {}
db_url = settings.DATABASE_URL

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif "supabase" in db_url or "sslmode=require" in db_url or "render.com" in db_url:
    # Clean sslmode from query string if present because asyncpg takes ssl in connect_args
    if "?sslmode=" in db_url:
        db_url = db_url.split("?sslmode=")[0]
    elif "&sslmode=" in db_url:
        db_url = db_url.split("&sslmode=")[0]
    connect_args["ssl"] = True

engine = create_async_engine(
    db_url,
    echo=False,
    connect_args=connect_args,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initializes tables if not created (useful for tests and SQLite local development)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
