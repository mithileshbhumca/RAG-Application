from datetime import UTC, datetime
from typing import Any, Protocol

from pydantic import BaseModel, Field

from app.document.models.contracts import DocumentAnalysisResult


class ProcessingRequest(BaseModel):
    document_id: str
    source_file: str
    media_type: str


class ProcessingResult(BaseModel):
    document_id: str
    processor_name: str
    extraction_method: str
    status: str = "completed"
    text_blocks: list[dict[str, Any]] = Field(default_factory=list)
    tables: list[dict[str, Any]] = Field(default_factory=list)
    images: list[dict[str, Any]] = Field(default_factory=list)
    layout_elements: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    processed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DocumentProcessor(Protocol):
    name: str

    def supports(self, analysis: DocumentAnalysisResult) -> bool: ...

    async def process(self, request: ProcessingRequest) -> ProcessingResult: ...
