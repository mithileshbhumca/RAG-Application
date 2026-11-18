import asyncio
import sqlite3
from pathlib import Path

from app.core.models.contracts import DocumentMetadata, IngestionStatus


class SQLiteDocumentRepository:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path = self.database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    source_file TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    byte_size INTEGER NOT NULL,
                    checksum_sha256 TEXT NOT NULL UNIQUE,
                    original_name TEXT NOT NULL,
                    document_version INTEGER NOT NULL,
                    registered_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS ingestion_status (
                    document_id TEXT PRIMARY KEY,
                    status_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    chunk_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_document_chunks_document
                    ON document_chunks(document_id);
                """
            )

    async def create_document(self, document: DocumentMetadata) -> DocumentMetadata:
        def operation() -> DocumentMetadata:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO documents
                    (document_id, source_file, media_type, byte_size, checksum_sha256,
                     original_name, document_version, registered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(document_id) DO UPDATE SET
                        source_file=excluded.source_file,
                        media_type=excluded.media_type,
                        byte_size=excluded.byte_size,
                        original_name=excluded.original_name,
                        document_version=excluded.document_version
                    """,
                    (
                        document.document_id,
                        document.source_file,
                        document.media_type,
                        document.byte_size,
                        document.checksum_sha256,
                        document.original_name,
                        document.document_version,
                        document.registered_at.isoformat(),
                    ),
                )
            return document

        return await asyncio.to_thread(operation)

    async def get_document(self, document_id: str) -> DocumentMetadata | None:
        def operation() -> DocumentMetadata | None:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM documents WHERE document_id = ?", (document_id,)
                ).fetchone()
            return self._row_to_document(row) if row else None

        return await asyncio.to_thread(operation)

    async def find_by_checksum(self, checksum: str) -> DocumentMetadata | None:
        def operation() -> DocumentMetadata | None:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM documents WHERE checksum_sha256 = ?", (checksum,)
                ).fetchone()
            return self._row_to_document(row) if row else None

        return await asyncio.to_thread(operation)

    @staticmethod
    def _row_to_document(row: sqlite3.Row) -> DocumentMetadata:
        return DocumentMetadata.model_validate(
            {
                "document_id": row["document_id"],
                "source_file": row["source_file"],
                "media_type": row["media_type"],
                "byte_size": row["byte_size"],
                "checksum_sha256": row["checksum_sha256"],
                "original_name": row["original_name"],
                "document_version": row["document_version"],
                "registered_at": row["registered_at"],
            }
        )

    async def save_status(self, status: IngestionStatus) -> None:
        def operation() -> None:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO ingestion_status (document_id, status_json, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(document_id) DO UPDATE SET
                        status_json=excluded.status_json,
                        updated_at=excluded.updated_at
                    """,
                    (
                        status.document_id,
                        status.model_dump_json(),
                        status.updated_at.isoformat(),
                    ),
                )

        await asyncio.to_thread(operation)

    async def get_status(self, document_id: str) -> IngestionStatus | None:
        def operation() -> IngestionStatus | None:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT status_json FROM ingestion_status WHERE document_id = ?", (document_id,)
                ).fetchone()
            return IngestionStatus.model_validate_json(row["status_json"]) if row else None

        return await asyncio.to_thread(operation)

    async def save_chunks(self, document_id: str, chunks: list[dict]) -> None:
        def operation() -> None:
            with self._connect() as connection:
                connection.execute(
                    "DELETE FROM document_chunks WHERE document_id = ?",
                    (document_id,),
                )
                connection.executemany(
                    """
                    INSERT INTO document_chunks (chunk_id, document_id, chunk_json)
                    VALUES (?, ?, ?)
                    """,
                    [
                        (chunk["chunk_id"], document_id, __import__("json").dumps(chunk))
                        for chunk in chunks
                    ],
                )

        await asyncio.to_thread(operation)

    async def get_chunks(self, document_id: str) -> list[dict]:
        def operation() -> list[dict]:
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT chunk_json FROM document_chunks WHERE document_id = ?",
                    (document_id,),
                ).fetchall()
            return [__import__("json").loads(row["chunk_json"]) for row in rows]

        return await asyncio.to_thread(operation)

    async def delete_document(self, document_id: str) -> None:
        def operation() -> None:
            with self._connect() as connection:
                connection.execute(
                    "DELETE FROM document_chunks WHERE document_id = ?",
                    (document_id,),
                )
                connection.execute(
                    "DELETE FROM ingestion_status WHERE document_id = ?",
                    (document_id,),
                )
                connection.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))

        await asyncio.to_thread(operation)
