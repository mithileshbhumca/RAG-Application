from pathlib import Path

from app.document.models.contracts import DocumentAnalysisResult
from app.processors.base.contracts import ProcessingRequest, ProcessingResult


class LayoutExtractionProcessor:
    name = "layout_extractor"

    def __init__(self, storage_root: Path):
        self.storage_root = storage_root

    def supports(self, analysis: DocumentAnalysisResult) -> bool:
        return True

    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        path = self.storage_root / request.source_file
        extension = path.suffix.lower()
        result = []
        if extension in {".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".md"}:
            result.append({
                "element_id": "layout-1",
                "element_type": "document",
                "heading_level": None,
                "reading_order": 1,
            })
        return ProcessingResult(
            document_id=request.document_id,
            processor_name=self.name,
            extraction_method="format_layout",
            layout_elements=result,
        )
