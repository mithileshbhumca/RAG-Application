from app.vector_store.base.contracts import (
    VectorRecord,
    VectorSearchRequest,
    VectorSearchResult,
)


class InMemoryVectorStore:
    def __init__(self):
        self.records: dict[str, VectorRecord] = {}

    async def ensure_collection(self, name: str, dimension: int) -> None:
        return None

    async def upsert(self, records: list[VectorRecord]) -> None:
        for record in records:
            self.records[record.chunk_id] = record

    async def search(self, request: VectorSearchRequest) -> list[VectorSearchResult]:
        return [
            VectorSearchResult(chunk_id=chunk_id, score=1.0, payload=record.payload)
            for chunk_id, record in list(self.records.items())[: request.limit]
        ]

    async def delete_document(self, document_id: str) -> None:
        self.records = {
            chunk_id: record
            for chunk_id, record in self.records.items()
            if record.payload.get("document_id") != document_id
        }

    async def delete_chunks(self, chunk_ids: list[str]) -> None:
        for chunk_id in chunk_ids:
            self.records.pop(chunk_id, None)
