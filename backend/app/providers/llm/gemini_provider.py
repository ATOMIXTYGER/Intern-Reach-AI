import json
import httpx
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from app.providers.llm.base import LLMProvider
from app.core.config import settings
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)

class GeminiProvider(LLMProvider):
    provider_name: str = "gemini"

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1500
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_class: Type[T],
        temperature: float = 0.2
    ) -> T:
        schema_json = json.dumps(schema_class.model_json_schema(), indent=2)
        augmented_system = (
            f"{system_prompt}\n\n"
            f"You must strictly output raw JSON matching this schema:\n{schema_json}\n"
            f"Do not include markdown code fences or conversational text. Output pure JSON."
        )

        for attempt in range(2):
            raw_text = await self.generate_text(
                system_prompt=augmented_system,
                user_prompt=user_prompt,
                temperature=temperature
            )
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            try:
                parsed_json = json.loads(clean_text)
                return schema_class.model_validate(parsed_json)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Gemini JSON validation failure (attempt {attempt + 1}): {e}")
                if attempt == 0:
                    user_prompt += f"\n\n[Correction]: Format error in prior output: {str(e)}. Return strictly valid JSON matching the schema."
                else:
                    raise ValueError(f"Failed to obtain valid structured output from Gemini: {str(e)}")
