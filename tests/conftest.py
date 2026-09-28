import os
import sys
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Set backend path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

os.environ["MOCK_MODE"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_internreach.db"

from main import app
from app.db.session import init_db, AsyncSessionLocal, engine
from app.db.base import Base
from app.db.seed import seed_database
from app.services.auth_service import get_user_by_email
from app.core.security import create_access_token

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_database()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    if os.path.exists("./test_internreach.db"):
        try:
            os.remove("./test_internreach.db")
        except Exception:
            pass

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def auth_headers():
    async with AsyncSessionLocal() as db:
        user = await get_user_by_email(db, "demo.student2028@internreach.ai")
        token = create_access_token(user.id)
        return {"Authorization": f"Bearer {token}"}
