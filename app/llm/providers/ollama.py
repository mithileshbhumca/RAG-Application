import httpx

from app.llm.base.contracts import (
    TextGenerationRequest,
    TextGenerationResult,
)


class OllamaProvider:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, request: TextGenerationRequest) -> TextGenerationResult:
        async with httpx.AsyncClient(timeout=request.timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": request.prompt,
                    "stream": False,
                    "options": {"temperature": request.temperature},
                },
            )
            response.raise_for_status()
            return TextGenerationResult(text=response.json()["response"], model=self.model)

    async def extract_structured(self, request, schema):
        prompt = (
            f"{request.prompt}\n\n"
            "Return only valid JSON matching this JSON schema:\n"
            f"{schema.model_json_schema()}"
        )
        result = await self.generate(TextGenerationRequest(
            prompt=prompt,
            temperature=request.temperature,
            timeout_seconds=request.timeout_seconds,
        ))
        return schema.model_validate_json(result.text)
