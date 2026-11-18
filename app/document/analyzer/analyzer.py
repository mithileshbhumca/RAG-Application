from pathlib import Path

import fitz
from PIL import Image

from app.document.models.contracts import DocumentAnalysisResult, DocumentDimensions


class DocumentAnalyzer:
    def __init__(self, storage_root: Path):
        self.storage_root = storage_root

    async def analyze(
        self,
        document_id: str,
        source_file: str,
        media_type: str,
    ) -> DocumentAnalysisResult:
        path = self.storage_root / source_file
        suffix = path.suffix.lower().lstrip(".")
        document_type = {
            "pdf": "pdf", "docx": "docx", "pptx": "pptx", "xlsx": "xlsx",
            "txt": "txt", "md": "markdown", "png": "image", "jpg": "image",
            "jpeg": "image", "tiff": "image", "tif": "image",
        }.get(suffix, "unknown")

        page_count = None
        dimensions = None
        contains_images = False
        contains_tables = False
        text_density = "none"
        is_scanned = False
        layout_complexity = "low"

        if document_type == "pdf":
            with fitz.open(path) as pdf:
                page_count = pdf.page_count
                native_chars = 0
                image_count = 0
                for page in pdf:
                    native_chars += len(page.get_text("text").strip())
                    image_count += len(page.get_images(full=True))
                    if page.get_drawings():
                        layout_complexity = "medium"
                first_rect = pdf[0].rect if page_count else None
                dimensions = DocumentDimensions(
                    width_points=first_rect.width if first_rect else None,
                    height_points=first_rect.height if first_rect else None,
                )
                is_scanned = native_chars < max(100, page_count * 20)
                text_density = self._density(native_chars, page_count)
                contains_images = image_count > 0

        elif document_type == "image":
            page_count = 1
            with Image.open(path) as image:
                dimensions = DocumentDimensions(
                    width_points=float(image.width),
                    height_points=float(image.height),
                )
                contains_images = True
            is_scanned = True

        elif document_type in {"docx", "pptx", "xlsx", "txt", "markdown"}:
            byte_size = path.stat().st_size
            text_density = "medium" if byte_size > 1000 else "low"

        processors = ["text_extractor"]
        if is_scanned:
            processors.append("ocr")
        if document_type == "pdf" and contains_images:
            processors.append("image_extractor")
        if document_type in {"docx", "pptx", "xlsx", "pdf"}:
            processors.append("layout_extractor")
        if document_type in {"pdf", "docx", "xlsx"}:
            processors.append("table_extractor")

        return DocumentAnalysisResult(
            document_id=document_id,
            document_type=document_type,
            media_type=media_type,
            is_scanned=is_scanned,
            page_count=page_count,
            dimensions=dimensions,
            contains_images=contains_images,
            contains_tables=contains_tables,
            text_density=text_density,
            layout_complexity=layout_complexity,
            recommended_processors=processors,
        )

    @staticmethod
    def _density(characters: int, pages: int) -> str:
        ratio = characters / max(pages, 1)
        if ratio < 20:
            return "none"
        if ratio < 500:
            return "low"
        if ratio < 3000:
            return "medium"
        return "high"
