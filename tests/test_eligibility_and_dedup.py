import pytest
from app.services.opportunity_service import deterministic_verify_opportunity

def test_eligibility_software_intern_2028():
    title = "Software Engineering Intern (Summer 2026)"
    jd = "Open to undergraduate students graduating in 2028 in Computer Science. Work with Python, FastAPI, and PostgreSQL."
    res = deterministic_verify_opportunity(title, jd, candidate_grad_year=2028, target_locations=["Bengaluru"])
    assert res.verified is True
    assert res.eligibility == "eligible"
    assert res.confidence >= 0.8

def test_eligibility_non_internship():
    title = "Senior Staff Software Engineer"
    jd = "Requires 10+ years of industry experience architecting distributed cloud systems."
    res = deterministic_verify_opportunity(title, jd, candidate_grad_year=2028)
    assert res.verified is False
    assert res.eligibility == "not_eligible"

def test_eligibility_non_technical():
    title = "Brand Marketing Intern"
    jd = "Manage social media posts and event sponsorships for campus brand ambassadors."
    res = deterministic_verify_opportunity(title, jd, candidate_grad_year=2028)
    assert res.verified is True
    assert res.eligibility == "not_eligible"

@pytest.mark.asyncio
async def test_opportunity_discovery_and_dedup_api(async_client, auth_headers):
    # Discovery API call
    payload = {
        "target_roles": ["Software Engineering Intern"],
        "graduation_year": 2028,
        "locations": ["Bengaluru"],
        "target_companies": ["Razorpay (Demo Data)"]
    }
    resp = await async_client.post("/api/v1/opportunities/search", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    results = resp.json()
    assert isinstance(results, list)

    # Calling search again should not duplicate existing records
    resp_again = await async_client.post("/api/v1/opportunities/search", json=payload, headers=auth_headers)
    assert resp_again.status_code == 200
    # Duplicate entries skipped
    assert len(resp_again.json()) == 0
