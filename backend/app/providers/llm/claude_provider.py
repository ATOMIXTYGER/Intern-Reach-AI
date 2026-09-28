import json
import httpx
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from app.providers.llm.base import LLMProvider
from app.core.config import settings
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)

class ClaudeProvider(LLMProvider):
    provider_name: str = "claude"

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1500
    ) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]

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
            f"You must strictly output raw JSON matching this JSON Schema:\n{schema_json}\n"
            f"Do not include markdown codeblocks or conversational prefix. Output only valid JSON."
        )

        for attempt in range(2): # Section 25: Retry once if malformed
            raw_text = await self.generate_text(
                system_prompt=augmented_system,
                user_prompt=user_prompt,
                temperature=temperature
            )
            # Clean markdown fences if any
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
                logger.warning(f"Claude JSON validation failure (attempt {attempt + 1}): {e}")
                if attempt == 0:
                    # Provide feedback on retry
                    user_prompt += f"\n\n[Correction]: The previous output was invalid JSON or did not match the required schema: {str(e)}. Please correct and return strictly the JSON object."
                else:
                    raise ValueError(f"Failed to obtain valid structured output from Claude: {str(e)}")
