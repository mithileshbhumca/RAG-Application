from pydantic import BaseModel, Field


class DocumentEnrichment(BaseModel):
    title: str | None = None
    document_type: str | None = None
    language: str | None = None
    summary: str | None = None
    entities: list[str] = Field(default_factory=list)
