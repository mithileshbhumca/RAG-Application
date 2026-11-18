from typing import Protocol, TypeVar

from pydantic import BaseModel


class TextGenerationRequest(BaseModel):
    prompt: str
    temperature: float = 0.0
    timeout_seconds: float = 30.0


class TextGenerationResult(BaseModel):
    text: str
    model: str


class StructuredExtractionRequest(BaseModel):
    prompt: str
    temperature: float = 0.0
    timeout_seconds: float = 30.0


T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    async def generate(self, request: TextGenerationRequest) -> TextGenerationResult: ...

    async def extract_structured(
        self,
        request: StructuredExtractionRequest,
        schema: type[T],
    ) -> T: ...


class VisionRequest(BaseModel):
    prompt: str
    image_paths: list[str]


class VisionResult(BaseModel):
    description: str
    model: str


class VisionProvider(Protocol):
    async def describe(self, request: VisionRequest) -> VisionResult: ...
