from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class DocumentDimensions(BaseModel):
    width_points: float | None = None
    height_points: float | None = None


class DocumentAnalysisResult(BaseModel):
    document_id: str
    document_type: str
    media_type: str
    is_scanned: bool = False
    page_count: int | None = None
    dimensions: DocumentDimensions | None = None
    contains_images: bool = False
    contains_tables: bool = False
    text_density: Literal["none", "low", "medium", "high"] = "none"
    layout_complexity: Literal["low", "medium", "high"] = "low"
    language_hint: str | None = None
    recommended_processors: list[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
