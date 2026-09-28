from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.opportunity import Opportunity
from app.models.contact import Contact
from app.models.outreach import OutreachMessage
from app.models.audit import SearchRun, AuditLog
from app.agents.workflow import internreach_graph
from app.agents.state import PipelineState
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin & Observability"])

@router.get("/diagnostics")
async def get_system_diagnostics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_opps = await db.scalar(select(func.count(Opportunity.id))) or 0
    total_contacts = await db.scalar(select(func.count(Contact.id))) or 0
    total_outreach = await db.scalar(select(func.count(OutreachMessage.id))) or 0
    search_runs = await db.scalar(select(func.count(SearchRun.id))) or 0

    return {
        "status": "healthy",
        "primary_llm": "configured",
        "mock_mode": True,
        "total_opportunities": total_opps,
        "total_contacts": total_contacts,
        "total_outreach_messages": total_outreach,
        "total_search_runs": search_runs
    }

@router.post("/run-pipeline-test")
async def run_pipeline_test(
    current_user: User = Depends(get_current_user)
):
    """Triggers the full LangGraph 10-node AI pipeline in memory to verify workflow"""
    initial_state = PipelineState(
        user_id=current_user.id,
        graduation_year=2028,
        target_roles=["Software Engineering Intern", "Backend Engineering Intern"],
        target_locations=["Bengaluru", "Remote"],
        target_companies=["Razorpay", "Swiggy", "CRED"],
        skills={"languages": ["Python", "Golang"], "frameworks": ["FastAPI"]}
    )

    final_state = await internreach_graph.ainvoke(initial_state)
    return {
        "success": True,
        "verified_count": len(final_state.get("verified_opportunities", [])),
        "contacts_researched": len(final_state.get("researched_contacts", [])),
        "drafts_generated": len(final_state.get("validated_drafts", [])),
        "awaiting_human_approval": final_state.get("awaiting_human_approval", True),
        "pipeline_logs": final_state.get("logs", [])
    }
