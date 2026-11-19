import asyncio
from pathlib import Path

import pymupdf
from PIL import Image

from app.document.models.contracts import DocumentAnalysisResult
from app.processors.base.contracts import ProcessingRequest, ProcessingResult


class ImageExtractionProcessor:
    name = "image_extractor"

    def __init__(self, storage_root: Path, artifact_root: Path):
        self.storage_root = storage_root
        self.artifact_root = artifact_root

    def supports(self, analysis: DocumentAnalysisResult) -> bool:
        return analysis.contains_images

    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        path = self.storage_root / request.source_file
        if path.suffix.lower() == ".pdf":
            images = await asyncio.to_thread(self._extract_pdf_images, path, request.document_id)
        else:
            output = self.artifact_root / request.document_id / "images" / path.name
            await asyncio.to_thread(output.parent.mkdir, parents=True, exist_ok=True)
            await asyncio.to_thread(Image.open(path).save, output)
            images = [{"page_number": 1, "image_id": path.stem, "storage_path": str(output)}]

        return ProcessingResult(
            document_id=request.document_id,
            processor_name=self.name,
            extraction_method="embedded_image_extraction",
            images=images,
        )

    def _extract_pdf_images(self, path: Path, document_id: str) -> list[dict]:
        result = []
        output_dir = self.artifact_root / document_id / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        with pymupdf.open(path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                for index, image_ref in enumerate(page.get_images(full=True), start=1):
                    xref = image_ref[0]
                    pixmap = pymupdf.Pixmap(pdf, xref)
                    if pixmap.n - pixmap.alpha > 4:
                        pixmap = pymupdf.Pixmap(pymupdf.csRGB, pixmap)
                    image_path = output_dir / f"p{page_number}-i{index}.png"
                    pixmap.save(image_path)
                    result.append({
                        "page_number": page_number,
                        "image_id": f"p{page_number}-i{index}",
                        "storage_path": str(image_path),
                    })
        return result
