from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class IngestionState(StrEnum):
    REGISTERED = "registered"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    NORMALIZING = "normalizing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    PARTIAL_COMPLETED = "partial_completed"
    FAILED = "failed"


class ProcessingError(BaseModel):
    stage: str
    processor_name: str | None = None
    code: str
    message: str
    retryable: bool = False
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class StageStatus(BaseModel):
    stage: str
    state: IngestionState
    started_at: datetime | None = None
    completed_at: datetime | None = None
    attempt_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentMetadata(BaseModel):
    document_id: str
    source_file: str
    media_type: str
    byte_size: int = Field(ge=0)
    checksum_sha256: str
    original_name: str
    document_version: int = 1
    registered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProcessingRequest(BaseModel):
    document_id: str
    source_file: str
    media_type: str
    document_version: int = 1
    options: dict[str, Any] = Field(default_factory=dict)


class IngestionStatus(BaseModel):
    document_id: str
    state: IngestionState
    stages: list[StageStatus] = Field(default_factory=list)
    errors: list[ProcessingError] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
