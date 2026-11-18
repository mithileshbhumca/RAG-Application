import pytest

from app.chunking.models.contracts import ChunkingConfig
from app.chunking.strategies.hierarchical import HierarchicalChunkingStrategy
from app.embeddings.providers.hash import DeterministicHashEmbeddingProvider
from app.knowledge.models.contracts import DocumentSection, NormalizedDocument, SourceReference


@pytest.mark.asyncio
async def test_hierarchical_chunks_preserve_parent_relationship():
    source = SourceReference(
        document_id="doc-1",
        source_file="doc-1/sample.txt",
        section_id="section-1",
        page_number=2,
        extraction_method="native",
        processor_name="text_extractor",
    )
    document = NormalizedDocument(
        document_id="doc-1",
        source_file="doc-1/sample.txt",
        document_type="txt",
        sections=[DocumentSection(
            section_id="section-1",
            heading="Introduction",
            content="A" * 700,
            page_numbers=[2],
            source=source,
        )],
    )

    result = HierarchicalChunkingStrategy().chunk(
        document,
        ChunkingConfig(child_size=500, overlap=100),
    )

    assert len(result.parents) == 1
    assert len(result.children) == 2
    assert result.children[0].parent_id == result.parents[0].chunk_id


@pytest.mark.asyncio
async def test_hash_embedding_is_normalized_and_dimensionally_consistent():
    provider = DeterministicHashEmbeddingProvider(dimension=32)
    result = await provider.embed_documents(["first document", "second document"])

    assert len(result.vectors) == 2
    assert len(result.vectors[0]) == 32
    assert abs(sum(value * value for value in result.vectors[0]) - 1.0) < 0.001
