# Vector store module

## Responsibility and implementation

The vector-store protocol and Pydantic request/record models live in
[`app/vector_store/base/contracts.py`](../../app/vector_store/base/contracts.py).
The API dependencies select the in-memory implementation by default or Qdrant when
configured.

- [`app/vector_store/base/memory.py`](../../app/vector_store/base/memory.py)
  stores records in a Python dictionary. Its `search()` returns the first records
  with a fixed score; it does not calculate similarity or apply filters. It is
  suitable only for demonstration/testing.
- [`app/vector_store/qdrant/store.py`](../../app/vector_store/qdrant/store.py)
  uses `qdrant-client` to create/check a cosine collection, upsert points, query
  nearest vectors, and delete by document or point IDs. Synchronous client
  operations are moved to worker threads. Although `VectorSearchRequest` includes
  filters, this adapter currently does not apply them.

## Libraries

**qdrant-client** provides the Qdrant adapter. Python `asyncio.to_thread` wraps
synchronous client calls; Pydantic defines the shared vector contract.

## Alternatives

Qdrant fits a dedicated vector service and is included in the Docker Compose setup.
Other options include PostgreSQL with pgvector or another managed/self-hosted
vector database. Compare filtering, payload/index behavior, operations, backup,
cost, and deployment fit.

## Production enhancements

- Add integration tests against the supported Qdrant version, especially point-ID
  compatibility, collection configuration, filtering, and deletion.
- Apply and validate metadata filters and tenant isolation.
- Plan collection migration/reindexing when the embedding model or dimension
  changes; the current adapter rejects dimension mismatches.
- Add timeouts, connection configuration, monitoring, backups, and restore testing.
- Define consistency and retry behavior for partial ingestion and document deletion.
- Do not use the in-memory adapter for real semantic retrieval or multi-process
  deployments.
