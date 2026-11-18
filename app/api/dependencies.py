from functools import lru_cache
from pathlib import Path

from app.chunking.models.contracts import ChunkingConfig
from app.chunking.strategies.hierarchical import HierarchicalChunkingStrategy
from app.core.config import get_settings
from app.document.analyzer.analyzer import DocumentAnalyzer
from app.embeddings.providers.hash import DeterministicHashEmbeddingProvider
from app.embeddings.providers.sentence_transformers import SentenceTransformerEmbeddingProvider
from app.knowledge.extraction.extractor import KnowledgeExtractor
from app.knowledge.normalization.normalizer import DocumentNormalizer
from app.llm.providers.disabled import DisabledLLMProvider
from app.llm.providers.ollama import OllamaProvider
from app.processors.images.image_processor import ImageExtractionProcessor
from app.processors.layout.layout_processor import LayoutExtractionProcessor
from app.processors.ocr.ocr_processor import TesseractOCRProcessor
from app.processors.registry.registry import ProcessorRegistry
from app.processors.tables.table_processor import TableExtractionProcessor
from app.processors.text.text_processor import TextExtractionProcessor
from app.storage.local.filesystem import LocalFilesystemStorage
from app.storage.metadata.sqlite import SQLiteDocumentRepository
from app.vector_store.base.memory import InMemoryVectorStore
from app.vector_store.qdrant.store import QdrantVectorStore


@lru_cache
def get_storage() -> LocalFilesystemStorage:
    return LocalFilesystemStorage(Path("./data/documents"))


def get_repository() -> SQLiteDocumentRepository:
    return SQLiteDocumentRepository(Path("./data/metadata.sqlite3"))


@lru_cache
def get_analyzer() -> DocumentAnalyzer:
    return DocumentAnalyzer(Path("./data/documents"))


@lru_cache
def get_processor_registry() -> ProcessorRegistry:
    root = Path("./data/documents")
    artifact_root = Path("./data/processed")
    registry = ProcessorRegistry()
    registry.register(TextExtractionProcessor(root))
    registry.register(TableExtractionProcessor(root))
    registry.register(ImageExtractionProcessor(root, artifact_root))
    registry.register(LayoutExtractionProcessor(root))
    registry.register(TesseractOCRProcessor(root))
    return registry


@lru_cache
def get_embedding_provider():
    settings = get_settings()
    if settings.embedding_provider == "sentence_transformers":
        return SentenceTransformerEmbeddingProvider(settings.embedding_model)
    return DeterministicHashEmbeddingProvider(settings.embedding_dimension)


@lru_cache
def get_vector_store():
    settings = get_settings()
    if settings.vector_store_provider == "qdrant":
        return QdrantVectorStore(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            collection_name=settings.qdrant_collection,
        )
    return InMemoryVectorStore()


@lru_cache
def get_chunking_strategy():
    return HierarchicalChunkingStrategy()


@lru_cache
def get_chunking_config() -> ChunkingConfig:
    return ChunkingConfig()


@lru_cache
def get_normalizer() -> DocumentNormalizer:
    return DocumentNormalizer()


@lru_cache
def get_knowledge_extractor() -> KnowledgeExtractor:
    settings = get_settings()
    if settings.llm_enabled and settings.llm_provider == "ollama":
        provider = OllamaProvider(settings.ollama_base_url, settings.llm_model)
        return KnowledgeExtractor(provider, enabled=True)
    return KnowledgeExtractor(DisabledLLMProvider(), enabled=False)
