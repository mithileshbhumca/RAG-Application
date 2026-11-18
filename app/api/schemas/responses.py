
from pydantic import BaseModel

from app.core.models.contracts import DocumentMetadata, IngestionStatus


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class DocumentMetadataResponse(BaseModel):
    document: DocumentMetadata


class DocumentStatusResponse(BaseModel):
    status: IngestionStatus


class UploadResponse(BaseModel):
    document: DocumentMetadata
    duplicate: bool
