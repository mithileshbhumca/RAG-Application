import asyncio

from app.embeddings.base.contracts import (
    EmbeddingModelMetadata,
    EmbeddingResult,
)


class SentenceTransformerEmbeddingProvider:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    async def embed_documents(self, texts: list[str]) -> EmbeddingResult:
        if not texts:
            return EmbeddingResult(
                vectors=[],
                metadata=EmbeddingModelMetadata(
                    provider="sentence_transformers",
                    model=self.model_name,
                    dimension=0,
                ),
            )

        def encode():
            model = self._load()
            vectors = model.encode(texts, normalize_embeddings=True).tolist()
            return vectors

        vectors = await asyncio.to_thread(encode)
        dimension = len(vectors[0])
        return EmbeddingResult(
            vectors=vectors,
            metadata=EmbeddingModelMetadata(
                provider="sentence_transformers",
                model=self.model_name,
                dimension=dimension,
            ),
        )

    async def embed_query(self, text: str) -> list[float]:
        result = await self.embed_documents([text])
        return result.vectors[0]
