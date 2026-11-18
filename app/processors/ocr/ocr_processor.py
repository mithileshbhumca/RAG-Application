import asyncio
import shutil
from pathlib import Path

import fitz

from app.document.models.contracts import DocumentAnalysisResult
from app.processors.base.contracts import ProcessingRequest, ProcessingResult


class TesseractOCRProcessor:
    name = "ocr"

    def __init__(self, storage_root: Path):
        self.storage_root = storage_root

    def supports(self, analysis: DocumentAnalysisResult) -> bool:
        return analysis.is_scanned

    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        if shutil.which("tesseract") is None:
            return ProcessingResult(
                document_id=request.document_id,
                processor_name=self.name,
                extraction_method="tesseract_cli",
                status="partial",
                warnings=["Tesseract executable is not installed"],
            )

        path = self.storage_root / request.source_file
        blocks = await asyncio.to_thread(self._ocr, path)
        return ProcessingResult(
            document_id=request.document_id,
            processor_name=self.name,
            extraction_method="tesseract_cli",
            text_blocks=blocks,
        )

    @staticmethod
    def _ocr(path: Path) -> list[dict]:
        import subprocess

        if path.suffix.lower() == ".pdf":
            with fitz.open(path) as pdf:
                pages = []
                for number, page in enumerate(pdf, start=1):
                    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    image_path = path.parent / f".{path.stem}-ocr-{number}.png"
                    pixmap.save(image_path)
                    completed = subprocess.run(
                        ["tesseract", str(image_path), "stdout", "--psm", "6"],
                        capture_output=True,
                        text=True,
                        timeout=120,
                        check=False,
                    )
                    image_path.unlink(missing_ok=True)
                    if completed.stdout.strip():
                        pages.append({
                            "page_number": number,
                            "block_id": f"ocr-p{number}",
                            "content": completed.stdout.strip(),
                            "confidence": None,
                        })
                return pages

        completed = subprocess.run(
            ["tesseract", str(path), "stdout", "--psm", "6"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if not completed.stdout.strip():
            return []
        return [{"page_number": 1, "block_id": "ocr-p1", "content": completed.stdout.strip()}]
