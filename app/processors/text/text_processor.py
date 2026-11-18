import asyncio
from pathlib import Path

import fitz
from docx import Document as DocxDocument
from pptx import Presentation

from app.document.models.contracts import DocumentAnalysisResult
from app.processors.base.contracts import ProcessingRequest, ProcessingResult


class TextExtractionProcessor:
    name = "text_extractor"

    def __init__(self, storage_root: Path):
        self.storage_root = storage_root

    def supports(self, analysis: DocumentAnalysisResult) -> bool:
        return True

    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        path = self.storage_root / request.source_file
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            blocks = await asyncio.to_thread(self._pdf_text, path)
        elif suffix == ".docx":
            blocks = await asyncio.to_thread(self._docx_text, path)
        elif suffix == ".pptx":
            blocks = await asyncio.to_thread(self._pptx_text, path)
        else:
            blocks = await asyncio.to_thread(self._plain_text, path)

        return ProcessingResult(
            document_id=request.document_id,
            processor_name=self.name,
            extraction_method="native",
            text_blocks=blocks,
        )

    @staticmethod
    def _pdf_text(path: Path) -> list[dict]:
        result = []
        with fitz.open(path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                for index, block in enumerate(page.get_text("blocks")):
                    text = block[4].strip()
                    if text:
                        result.append({
                            "page_number": page_number,
                            "block_id": f"p{page_number}-b{index}",
                            "content": text,
                            "bbox": list(block[:4]),
                        })
        return result

    @staticmethod
    def _docx_text(path: Path) -> list[dict]:
        result = []
        document = DocxDocument(path)
        for index, paragraph in enumerate(document.paragraphs):
            if paragraph.text.strip():
                result.append({
                    "page_number": None,
                    "block_id": f"p{index}",
                    "content": paragraph.text.strip(),
                })
        return result

    @staticmethod
    def _pptx_text(path: Path) -> list[dict]:
        result = []
        presentation = Presentation(path)
        for slide_number, slide in enumerate(presentation.slides, start=1):
            for index, shape in enumerate(slide.shapes):
                if getattr(shape, "has_text_frame", False):
                    text = shape.text.strip()
                    if text:
                        result.append({
                            "page_number": slide_number,
                            "block_id": f"s{slide_number}-b{index}",
                            "content": text,
                        })
        return result

    @staticmethod
    def _plain_text(path: Path) -> list[dict]:
        text = path.read_text(encoding="utf-8", errors="replace")
        return [{"page_number": None, "block_id": "text-0", "content": text}]
