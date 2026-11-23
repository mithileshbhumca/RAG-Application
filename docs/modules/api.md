# API module

## Responsibility and implementation

The API is the FastAPI boundary for document registration and lifecycle operations.
`app/main.py` creates the app, attaches the health and document routers, and maps
domain exceptions to HTTP responses.

[`app/api/routes/documents.py`](../../app/api/routes/documents.py) implements:

- `POST /api/v1/documents/upload`: reads the upload, checks emptiness, configured
  size and MIME allowlist, hashes the bytes with SHA-256, detects duplicate
  checksums, and stores a new document and initial status.
- `POST /api/v1/documents/{document_id}/ingest`: constructs the orchestrator and
  runs ingestion in the request.
- `GET` routes for status, metadata, and chunks, plus document deletion.

[`app/api/dependencies.py`](../../app/api/dependencies.py) wires concrete
implementations: local files, SQLite, processors, embedding, LLM, and vector-store
adapters. The health endpoint reports service configuration; it is not a dependency
readiness check.

## Libraries

- **FastAPI** supplies routing, dependency injection, and HTTP exception handling.
- **Pydantic** models shared request/response data.
- Python standard-library `hashlib`, `mimetypes`, and `pathlib` support upload
  checks and storage-key construction.

## Alternatives

Keep the API framework-independent from business logic by delegating work to
services. FastAPI is already suitable for this boundary; Starlette or another ASGI
framework is an alternative if the application has different framework needs.

## Production enhancements

- Stream uploads to avoid holding full files in memory; enforce limits while
  streaming and validate actual file content in addition to the client MIME type.
- Run ingestion as a durable background job and return a job/status resource rather
  than holding an HTTP request open.
- Add authentication, authorization, quotas, rate limits, request IDs, and
  structured error responses.
- Make readiness checks test actual required dependencies separately from liveness.
- Complete deletion across metadata, vectors, original files, and processed
  artifacts with safe retry behavior.

There is no question-answering or retrieval endpoint yet; see the root
[README implementation status](../../README.md#15-current-implementation-status).
