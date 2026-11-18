from pathlib import Path

from app.chunking.models.contracts import ChunkingConfig
from app.chunking.strategies.base import ChunkingStrategy
from app.core.models.contracts import IngestionState, IngestionStatus
from app.document.analyzer.analyzer import DocumentAnalyzer
from app.embeddings.base.contracts import EmbeddingProvider
from app.knowledge.extraction.extractor import KnowledgeExtractor
from app.knowledge.normalization.normalizer import DocumentNormalizer
from app.processors.base.contracts import ProcessingRequest
from app.processors.registry.registry import ProcessorRegistry
from app.storage.metadata.sqlite import SQLiteDocumentRepository
from app.vector_store.base.contracts import VectorRecord, VectorStore


class IngestionOrchestrator:
    def __init__(
        self,
        repository: SQLiteDocumentRepository,
        analyzer: DocumentAnalyzer,
        registry: ProcessorRegistry,
        normalizer: DocumentNormalizer,
        knowledge_extractor: KnowledgeExtractor,
        chunking_strategy: ChunkingStrategy,
        chunking_config: ChunkingConfig,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        storage_root: Path,
    ):
        self.repository = repository
        self.analyzer = analyzer
        self.registry = registry
        self.normalizer = normalizer
        self.knowledge_extractor = knowledge_extractor
        self.chunking_strategy = chunking_strategy
        self.chunking_config = chunking_config
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.storage_root = storage_root

    async def ingest(self, document_id: str) -> IngestionStatus:
        document = await self.repository.get_document(document_id)
        if document is None:
            raise LookupError(document_id)

        status = IngestionStatus(document_id=document_id, state=IngestionState.ANALYZING)
        await self.repository.save_status(status)

        analysis = await self.analyzer.analyze(
            document_id=document_id,
            source_file=document.source_file,
            media_type=document.media_type,
        )

        status.state = IngestionState.PROCESSING
        await self.repository.save_status(status)

        results = []
        for processor in self.registry.for_analysis(analysis):
            result = await processor.process(ProcessingRequest(
                document_id=document_id,
                source_file=document.source_file,
                media_type=document.media_type,
            ))
            results.append(result)

        status.state = IngestionState.NORMALIZING
        await self.repository.save_status(status)

        normalized = self.normalizer.normalize(analysis, document.source_file, results)
        enrichment = await self.knowledge_extractor.enrich(normalized)
        normalized.title = enrichment.title or normalized.title
        normalized.metadata["llm_enrichment"] = enrichment.model_dump()
        normalized_path = self.storage_root.parent / "processed" / document_id
        normalized_path.mkdir(parents=True, exist_ok=True)
        (normalized_path / "normalized.json").write_text(
            normalized.model_dump_json(indent=2), encoding="utf-8"
        )

        status.state = IngestionState.CHUNKING
        await self.repository.save_status(status)
        chunking = self.chunking_strategy.chunk(normalized, self.chunking_config)

        status.state = IngestionState.EMBEDDING
        await self.repository.save_status(status)
        chunks = [*chunking.parents, *chunking.children]
        texts = [chunk.content for chunk in chunks]
        embedding_result = await self.embedding_provider.embed_documents(texts)

        if len(embedding_result.vectors) != len(chunks):
            raise ValueError("Embedding provider returned an unexpected number of vectors")

        records = []
        for chunk, vector in zip(chunks, embedding_result.vectors, strict=True):
            records.append(VectorRecord(
                chunk_id=chunk.chunk_id,
                vector=vector,
                payload={
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.chunk_id,
                    "parent_id": chunk.parent_id,
                    "section_id": chunk.section_id,
                    "page_number": chunk.page_numbers,
                    "source_file": document.source_file,
                    "content_type": chunk.content_type,
                    "document_type": document.media_type,
                    "extraction_method": chunk.metadata.get("extraction_method", "unknown"),
                    "embedding_model": embedding_result.metadata.model,
                    "document_version": document.document_version,
                },
            ))

        status.state = IngestionState.INDEXING
        await self.repository.save_status(status)
        await self.vector_store.ensure_collection(
            "document_chunks",
            embedding_result.metadata.dimension,
        )
        await self.vector_store.upsert(records)
        await self.repository.save_chunks(
            document_id,
            [chunk.model_dump(mode="json") for chunk in chunks],
        )

        partial = any(result.status == "partial" for result in results)
        status.state = (
            IngestionState.PARTIAL_COMPLETED if partial else IngestionState.COMPLETED
        )
        await self.repository.save_status(status)
        return status
