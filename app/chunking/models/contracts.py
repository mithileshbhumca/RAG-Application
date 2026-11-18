from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class ChunkingConfig(BaseModel):
    strategy: str = "hierarchical"
    parent_size: int = Field(default=2000, gt=0)
    child_size: int = Field(default=500, gt=0)
    overlap: int = Field(default=100, ge=0)


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    parent_id: str | None = None
    section_id: str | None = None
    content: str
    content_type: str = "text"
    page_numbers: list[int] = Field(default_factory=list)
    heading_context: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ParentChunk(Chunk):
    child_ids: list[str] = Field(default_factory=list)


class ChunkingResult(BaseModel):
    parents: list[ParentChunk] = Field(default_factory=list)
    children: list[Chunk] = Field(default_factory=list)
