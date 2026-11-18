from app.llm.base.contracts import TextGenerationRequest, TextGenerationResult


class DisabledLLMProvider:
    @property
    def model(self) -> str:
        return "disabled"

    async def generate(self, request: TextGenerationRequest) -> TextGenerationResult:
        return TextGenerationResult(text="", model="disabled")

    async def extract_structured(self, request, schema):
        raise RuntimeError("LLM enrichment is disabled")
