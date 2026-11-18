from app.embeddings.base.contracts import EmbeddingModelMetadata, EmbeddingResult


class DeterministicHashEmbeddingProvider:
    """Lightweight provider for local development and tests; never use for production retrieval."""

    def __init__(self, dimension: int = 64):
        self.dimension = dimension

    async def embed_documents(self, texts: list[str]) -> EmbeddingResult:
        vectors = []
        for text in texts:
            vector = [0.0] * self.dimension
            for index, byte in enumerate(text.encode("utf-8")):
                vector[(index * 31 + byte) % self.dimension] += 1.0
            length = sum(value * value for value in vector) ** 0.5
            if length:
                vector = [value / length for value in vector]
            vectors.append(vector)
        return EmbeddingResult(
            vectors=vectors,
            metadata=EmbeddingModelMetadata(
                provider="deterministic_hash",
                model="deterministic-v1",
                dimension=self.dimension,
            ),
        )

    async def embed_query(self, text: str) -> list[float]:
        result = await self.embed_documents([text])
        return result.vectors[0]
