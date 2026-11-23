# Application Module Guides

These guides describe the implementation currently present in `app/`, name the
libraries used at each boundary, and distinguish implemented behavior from possible
alternatives and production enhancements. Recommendations are not implemented
features. For current limitations and validation status, see the root
[README](../../README.md).

| Module | Responsibility |
|---|---|
| [API](api.md) | FastAPI routes, request validation, and dependency wiring |
| [Chunking](chunking.md) | Chunk contracts and hierarchical chunk generation |
| [Core](core.md) | Settings, shared contracts, errors, logging, and protocols |
| [Document](document.md) | File analysis and document-analysis contracts |
| [Embeddings](embeddings.md) | Embedding protocol and provider adapters |
| [Ingestion](ingestion.md) | Pipeline orchestration and job placeholder |
| [Knowledge](knowledge.md) | Normalization and optional structured enrichment |
| [LLM](llm.md) | Text-generation contracts and Ollama adapter |
| [Processors](processors.md) | Text, table, image, OCR, and layout extraction |
| [Storage](storage.md) | Local file storage and SQLite metadata repository |
| [Vector store](vector-store.md) | In-memory and Qdrant vector adapters |

## End-to-end path

The API registers a file in local storage and SQLite. An explicit ingest request
then runs the analyzer and supported processors; normalization combines their
results, optional enrichment runs, and the chunking, embedding, vector-store, and
metadata-repository adapters persist the resulting records. The current pipeline is
synchronous and should be treated as an MVP, not a production-ready distributed
worker system.
