from typing import Any, Protocol

from pydantic import BaseModel, Field


class VectorRecord(BaseModel):
    chunk_id: str
    vector: list[float]
    payload: dict[str, Any]


class VectorSearchRequest(BaseModel):
    vector: list[float]
    limit: int = Field(default=10, gt=0)
    filters: dict[str, Any] = Field(default_factory=dict)


class VectorSearchResult(BaseModel):
    chunk_id: str
    score: float
    payload: dict[str, Any]


class VectorStore(Protocol):
    async def ensure_collection(self, name: str, dimension: int) -> None: ...
    async def upsert(self, records: list[VectorRecord]) -> None: ...
    async def search(self, request: VectorSearchRequest) -> list[VectorSearchResult]: ...
    async def delete_document(self, document_id: str) -> None: ...
    async def delete_chunks(self, chunk_ids: list[str]) -> None: ...
