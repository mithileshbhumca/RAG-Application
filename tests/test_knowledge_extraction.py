import pytest

from app.knowledge.extraction.contracts import DocumentEnrichment
from app.knowledge.extraction.extractor import KnowledgeExtractor
from app.knowledge.models.contracts import DocumentSection, NormalizedDocument, SourceReference


class MockLLM:
    async def extract_structured(self, request, schema):
        return schema.model_validate({"title": "Mock title", "summary": "Mock summary"})


@pytest.mark.asyncio
async def test_disabled_extraction_preserves_source_document():
    source = SourceReference(
        document_id="doc-1",
        source_file="doc-1/sample.txt",
        extraction_method="native",
        processor_name="text_extractor",
    )
    document = NormalizedDocument(
        document_id="doc-1",
        source_file="doc-1/sample.txt",
        document_type="txt",
        sections=[DocumentSection(section_id="s1", content="Original text", source=source)],
    )

    enrichment = await KnowledgeExtractor(MockLLM(), enabled=False).enrich(document)

    assert isinstance(enrichment, DocumentEnrichment)
    assert enrichment.title is None
    assert document.sections[0].content == "Original text"


@pytest.mark.asyncio
async def test_enabled_extraction_returns_validated_schema():
    source = SourceReference(
        document_id="doc-1",
        source_file="doc-1/sample.txt",
        extraction_method="native",
        processor_name="text_extractor",
    )
    document = NormalizedDocument(
        document_id="doc-1",
        source_file="doc-1/sample.txt",
        document_type="txt",
        sections=[DocumentSection(section_id="s1", content="Original text", source=source)],
    )

    enrichment = await KnowledgeExtractor(MockLLM(), enabled=True).enrich(document)

    assert enrichment.title == "Mock title"
    assert enrichment.summary == "Mock summary"
