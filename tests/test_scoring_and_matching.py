import pytest
from app.models.candidate import CandidateProfile
from app.models.opportunity import Opportunity
from app.services.matching_service import compute_match_scores

def test_deterministic_matching_algorithm():
    profile = CandidateProfile(
        user_id="test-user",
        full_name="Arjun Mehta",
        graduation_year=2028,
        preferred_locations=["Bengaluru", "Remote"],
        target_roles=["Software Engineering Intern", "Backend Engineering Intern"],
        skills={"languages": ["Python", "Golang", "SQL"], "frameworks": ["FastAPI", "React"]},
        experiences={
            "projects": [
                {"title": "FastAPI Distributed System", "technologies": ["Python", "FastAPI", "PostgreSQL"]}
            ]
        }
    )
    opp = Opportunity(
        company_name="Razorpay (Demo Data)",
        title="Software Engineering Intern - Payments Core",
        job_description="Looking for 2028 engineering students proficient in Python, FastAPI, and SQL.",
        location="Bengaluru, India",
        application_url="https://careers.razorpay.com/demo",
        required_skills=["Python", "FastAPI", "SQL"],
        preferred_skills=["Golang"],
        eligibility_status="eligible",
        verified=True
    )

    scores = compute_match_scores(profile, opp)
    assert scores["overall_match_score"] >= 80.0
    assert "Python" in scores["matched_skills"]
    assert "FastAPI" in scores["matched_skills"]
    assert len(scores["missing_skills"]) == 0
    assert len(scores["relevant_projects"]) >= 1

@pytest.mark.asyncio
async def test_matching_api(async_client, auth_headers):
    # Fetch an opportunity
    opps_resp = await async_client.get("/api/v1/opportunities", headers=auth_headers)
    assert opps_resp.status_code == 200
    opps = opps_resp.json()
    assert len(opps) > 0
    first_opp_id = opps[0]["id"]

    # Run match
    match_resp = await async_client.post(f"/api/v1/matches/{first_opp_id}", headers=auth_headers)
    assert match_resp.status_code == 200
    data = match_resp.json()
    assert "overall_match_score" in data
    assert data["opportunity_id"] == first_opp_id
