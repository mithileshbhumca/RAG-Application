from app.document.models.contracts import DocumentAnalysisResult
from app.knowledge.models.contracts import DocumentSection, NormalizedDocument, SourceReference
from app.processors.base.contracts import ProcessingResult


class DocumentNormalizer:
    def normalize(
        self,
        analysis: DocumentAnalysisResult,
        source_file: str,
        results: list[ProcessingResult],
    ) -> NormalizedDocument:
        sections = []
        tables = []
        images = []

        for result in results:
            for block in result.text_blocks:
                page_number = block.get("page_number")
                section_id = f"{result.processor_name}-{block.get('block_id', len(sections))}"
                source = SourceReference(
                    document_id=analysis.document_id,
                    source_file=source_file,
                    page_number=page_number,
                    section_id=section_id,
                    extraction_method=result.extraction_method,
                    processor_name=result.processor_name,
                )
                sections.append(DocumentSection(
                    section_id=section_id,
                    content=str(block.get("content", "")),
                    page_numbers=[page_number] if isinstance(page_number, int) else [],
                    source=source,
                ))

            for table in result.tables:
                tables.append({**table, "processor_name": result.processor_name,
                               "extraction_method": result.extraction_method})
            for image in result.images:
                images.append({**image, "processor_name": result.processor_name,
                               "extraction_method": result.extraction_method})

        return NormalizedDocument(
            document_id=analysis.document_id,
            source_file=source_file,
            document_type=analysis.document_type,
            sections=sections,
            tables=tables,
            images=images,
            metadata={
                "is_scanned": analysis.is_scanned,
                "page_count": analysis.page_count,
                "text_density": analysis.text_density,
                "layout_complexity": analysis.layout_complexity,
                "language_hint": analysis.language_hint,
            },
        )
