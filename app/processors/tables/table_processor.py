import asyncio
from pathlib import Path

from openpyxl import load_workbook

from app.document.models.contracts import DocumentAnalysisResult
from app.processors.base.contracts import ProcessingRequest, ProcessingResult


class TableExtractionProcessor:
    name = "table_extractor"

    def __init__(self, storage_root: Path):
        self.storage_root = storage_root

    def supports(self, analysis: DocumentAnalysisResult) -> bool:
        return analysis.document_type in {"pdf", "docx", "xlsx"}

    async def process(self, request: ProcessingRequest) -> ProcessingResult:
        path = self.storage_root / request.source_file
        if path.suffix.lower() == ".xlsx":
            tables = await asyncio.to_thread(self._xlsx_tables, path)
        else:
            tables = []
        return ProcessingResult(
            document_id=request.document_id,
            processor_name=self.name,
            extraction_method="format_native",
            tables=tables,
        )

    @staticmethod
    def _xlsx_tables(path: Path) -> list[dict]:
        workbook = load_workbook(path, data_only=True)
        tables = []
        for sheet in workbook.worksheets:
            rows = []
            for row in sheet.iter_rows(values_only=True):
                rows.append(["" if value is None else str(value) for value in row])
            if rows:
                headers = rows[0]
                tables.append({
                    "table_id": f"sheet-{sheet.title}",
                    "sheet_name": sheet.title,
                    "headers": headers,
                    "rows": rows[1:],
                    "markdown": TableExtractionProcessor._to_markdown(headers, rows[1:]),
                })
        return tables

    @staticmethod
    def _to_markdown(headers: list[str], rows: list[list[str]]) -> str:
        header_row = "| " + " | ".join(headers) + " |"
        separator = "| " + " | ".join("---" for _ in headers) + " |"
        body = ["| " + " | ".join(row) + " |" for row in rows]
        return "\n".join([header_row, separator, *body])
