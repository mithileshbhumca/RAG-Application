from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    document_id: str
    source_file: str
    page_number: int | None = None
    section_id: str | None = None
    extraction_method: str
    processor_name: str


class DocumentSection(BaseModel):
    section_id: str
    heading: str | None = None
    level: int = 0
    content: str
    page_numbers: list[int] = Field(default_factory=list)
    source: SourceReference


class NormalizedDocument(BaseModel):
    document_id: str
    source_file: str
    document_type: str
    title: str | None = None
    sections: list[DocumentSection] = Field(default_factory=list)
    tables: list[dict[str, Any]] = Field(default_factory=list)
    images: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    normalized_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
