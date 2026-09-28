import pytest
from app.agents.workflow import internreach_graph
from app.agents.state import PipelineState

@pytest.mark.asyncio
async def test_langgraph_agent_pipeline_e2e():
    initial_state = PipelineState(
        user_id="test-student-2028",
        graduation_year=2028,
        target_roles=["Software Engineering Intern", "Backend Engineering Intern", "AI/ML Engineering Intern"],
        target_locations=["Bengaluru", "Remote"],
        target_companies=["Razorpay", "CRED", "Swiggy"],
        skills={
            "languages": ["Python", "Golang", "TypeScript"],
            "frameworks": ["FastAPI", "Next.js", "React"]
        }
    )

    final_state = await internreach_graph.ainvoke(initial_state)

    # Assert all nodes executed properly
    assert len(final_state["raw_discovered"]) > 0
    assert len(final_state["deduplicated_opportunities"]) > 0
    assert len(final_state["verified_opportunities"]) > 0
    assert len(final_state["eligible_opportunities"]) > 0
    assert len(final_state["researched_contacts"]) > 0
    assert len(final_state["matches"]) > 0
    assert len(final_state["outreach_drafts"]) > 0
    assert len(final_state["validated_drafts"]) > 0

    # Ensure Human-in-the-loop requirement
    assert final_state["awaiting_human_approval"] is True

    # Check logs
    assert any("Discovered" in log for log in final_state["logs"])
    assert any("human approval" in log for log in final_state["logs"])
