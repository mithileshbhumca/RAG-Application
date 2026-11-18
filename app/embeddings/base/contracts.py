from typing import Protocol

from pydantic import BaseModel


class EmbeddingModelMetadata(BaseModel):
    provider: str
    model: str
    dimension: int


class EmbeddingResult(BaseModel):
    vectors: list[list[float]]
    metadata: EmbeddingModelMetadata


class EmbeddingProvider(Protocol):
    async def embed_documents(self, texts: list[str]) -> EmbeddingResult: ...

    async def embed_query(self, text: str) -> list[float]: ...
