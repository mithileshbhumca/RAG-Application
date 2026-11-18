import asyncio

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.vector_store.base.contracts import (
    VectorRecord,
    VectorSearchRequest,
    VectorSearchResult,
)


class QdrantVectorStore:
    def __init__(
        self,
        url: str,
        api_key: str | None = None,
        collection_name: str = "document_chunks",
    ):
        self._client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name

    async def ensure_collection(self, name: str, dimension: int) -> None:
        def operation():
            if self._client.collection_exists(self.collection_name):
                info = self._client.get_collection(self.collection_name)
                size = info.config.params.vectors.size
                if size != dimension:
                    raise ValueError(
                        f"Collection '{self.collection_name}' dimension {size} "
                        f"does not match model dimension {dimension}"
                    )
                return
            self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=dimension, distance=models.Distance.COSINE),
            )

        await asyncio.to_thread(operation)

    async def upsert(self, records: list[VectorRecord]) -> None:
        if not records:
            return
        points = [
            models.PointStruct(id=record.chunk_id, vector=record.vector, payload=record.payload)
            for record in records
        ]

        await asyncio.to_thread(
            self._client.upsert,
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

    async def search(self, request: VectorSearchRequest) -> list[VectorSearchResult]:
        def operation():
            hits = self._client.query_points(
                collection_name=self.collection_name,
                query=request.vector,
                limit=request.limit,
                with_payload=True,
            ).points
            return [
                VectorSearchResult(
                    chunk_id=str(hit.id),
                    score=float(hit.score),
                    payload=hit.payload or {},
                )
                for hit in hits
            ]

        return await asyncio.to_thread(operation)

    async def delete_document(self, document_id: str) -> None:
        await asyncio.to_thread(
            self._client.delete,
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
            wait=True,
        )

    async def delete_chunks(self, chunk_ids: list[str]) -> None:
        await asyncio.to_thread(
            self._client.delete,
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(points=chunk_ids),
            wait=True,
        )
