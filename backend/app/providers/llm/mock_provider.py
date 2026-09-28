import re
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from app.providers.llm.base import LLMProvider
from app.schemas.outreach import LLMMessageResponse
from app.schemas.opportunity import VerificationResult
from app.schemas.match import MatchResultOut

T = TypeVar("T", bound=BaseModel)

class MockLLMProvider(LLMProvider):
    provider_name: str = "mock"

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1500
    ) -> str:
        return (
            "Hi, I noticed the Software Engineering internship at your company for Summer 2026. "
            "As a 2028 engineering graduate with hands-on experience building distributed backend microservices "
            "and AI systems, I would appreciate any guidance on the application process. Thank you!"
        )

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_class: Type[T],
        temperature: float = 0.2
    ) -> T:
        class_name = schema_class.__name__

        if "LLMMessageResponse" in class_name:
            # Deterministic, high-quality message compliant with Section 12
            # Check strategy / channel keywords
            is_referral = "referral" in user_prompt.lower()
            is_followup = "follow-up" in user_prompt.lower() or "followup" in user_prompt.lower()

            if is_followup:
                data = {
                    "message": (
                        "Hi, I wanted to follow up briefly regarding my previous note about the Software Engineering internship. "
                        "I understand you are likely busy, but would love to know if 2028 engineering undergraduates are currently being considered. "
                        "Thanks again for your time and guidance."
                    ),
                    "personalization_reason": "Respectful polite follow-up after 7 days referencing previous context and 2028 graduation timeline.",
                    "evidence_used": ["Previous outreach record", "Public early careers recruiting window"],
                    "confidence": 0.92
                }
            elif is_referral:
                data = {
                    "message": (
                        "Hi, I saw your work on the core engineering team and noticed the upcoming Software Engineering Internship. "
                        "I am an engineering student graduating in 2028 with background in FastAPI, PostgreSQL, and scalable microservices. "
                        "If you feel my profile aligns, would you be open to an optional referral or sharing any pointers on the role? "
                        "No worries if not, and thanks for your time!"
                    ),
                    "personalization_reason": "Targeted alumni/engineer peer connection highlighting matched backend skills and polite optional referral inquiry.",
                    "evidence_used": ["Current engineering team member profile", "Published internship listing requirements"],
                    "confidence": 0.88
                }
            else:
                data = {
                    "message": (
                        "Hi, I saw your role coordinating early-career talent and wanted to inquire about the Software Engineering Internship. "
                        "I am a 2028 engineering student with practical experience building async Python services and full-stack applications. "
                        "Could you share if sophomore undergraduates are eligible for this recruitment cycle? Appreciate any guidance!"
                    ),
                    "personalization_reason": "Tailored to early careers recruiter; explicitly mentions 2028 graduation year, matches backend skills, and asks for guidance respectfully.",
                    "evidence_used": ["Public recruiter title: University / Early Careers Talent Partner", "Verified active internship listing"],
                    "confidence": 0.95
                }
            return schema_class.model_validate(data)

        if "VerificationResult" in class_name:
            data = {
                "verified": True,
                "eligibility": "eligible",
                "confidence": 0.94,
                "reasons": [
                    "Public listing confirms software engineering internship active role",
                    "Targeted towards 2027/2028 batch engineering undergraduates",
                    "Location verified in India / Remote tech center"
                ],
                "evidence": [
                    "Direct careers portal posting",
                    "Official requirements match software development fundamentals"
                ]
            }
            return schema_class.model_validate(data)

        # Default fallback for other models (e.g. structured resume or generic match)
        return schema_class.model_construct()
