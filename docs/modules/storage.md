# Storage module

## Responsibility and implementation

The storage module provides local file and metadata adapters.

[`app/storage/local/filesystem.py`](../../app/storage/local/filesystem.py)
implements `LocalFilesystemStorage`. It rejects absolute keys and `..` path
components, then performs file reads/writes in worker threads with
`asyncio.to_thread`. Uploaded originals are stored under document-specific paths.
The metadata argument to `put()` is accepted by the interface but is not persisted
by this adapter.

[`app/storage/metadata/sqlite.py`](../../app/storage/metadata/sqlite.py)
implements `SQLiteDocumentRepository`. It initializes tables for documents,
ingestion status, and serialized chunks; database work runs in worker threads.
The repository enforces a unique checksum and stores status/chunk JSON. SQLite
connections are opened per operation. Document deletion removes repository rows,
but the API currently does not remove original files and processed artifacts.

## Libraries

**SQLite** uses Python's built-in `sqlite3`; file operations use Python
`pathlib` and `asyncio`. **Pydantic** validates records read from the database.

## Alternatives

For local development, this combination avoids external infrastructure. Production
alternatives include PostgreSQL for concurrent relational metadata and an
object-storage service for durable, scalable documents. Preserve the existing
repository and object-storage protocols when adding adapters.

## Production enhancements

- Use database migrations, transactional consistency, indexes, backups, and tested
  restore procedures.
- Stream large files and use atomic writes, checksums, and immutable object keys.
- Enforce tenant/access boundaries and retention/deletion policy.
- Persist supplied metadata or remove it from the adapter contract if not needed.
- Coordinate file, metadata, vector, and artifact deletion with retryable cleanup.
- Add concurrency and failure tests; SQLite may become a bottleneck under
  multi-worker write load.
