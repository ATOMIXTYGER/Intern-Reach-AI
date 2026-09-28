import pytest
import io

@pytest.mark.asyncio
async def test_auth_registration_and_login(async_client):
    reg_payload = {
        "email": "new.student2028@internreach.ai",
        "password": "StrongPassword2028!",
        "full_name": "Rohan Sharma"
    }
    # 1. Register
    reg_resp = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    data = reg_resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "new.student2028@internreach.ai"

    # 2. Login
    login_resp = await async_client.post("/api/v1/auth/login", json={
        "email": "new.student2028@internreach.ai",
        "password": "StrongPassword2028!"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # 3. Invalid Login
    bad_login = await async_client.post("/api/v1/auth/login", json={
        "email": "new.student2028@internreach.ai",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

@pytest.mark.asyncio
async def test_unauthorized_access(async_client):
    # Calling protected endpoint without token must return 401
    resp = await async_client.get("/api/v1/candidate")
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_candidate_profile_crud(async_client, auth_headers):
    # Fetch candidate profile
    resp = await async_client.get("/api/v1/candidate", headers=auth_headers)
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["graduation_year"] == 2028
    assert "Software Engineering Intern" in profile["target_roles"]

    # Update profile
    profile["university"] = "IIT Bombay (Verified)"
    profile["graduation_year"] = 2028
    update_resp = await async_client.put("/api/v1/candidate", json=profile, headers=auth_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["university"] == "IIT Bombay (Verified)"

@pytest.mark.asyncio
async def test_resume_upload(async_client, auth_headers):
    import pypdf
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)
    pdf_bytes = buf.getvalue()
    
    files = {"file": ("my_resume.pdf", pdf_bytes, "application/pdf")}
    
    resp = await async_client.post("/api/v1/candidate/resume", files=files, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
