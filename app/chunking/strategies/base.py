from typing import Protocol

from app.chunking.models.contracts import ChunkingConfig, ChunkingResult
from app.knowledge.models.contracts import NormalizedDocument


class ChunkingStrategy(Protocol):
    name: str

    def chunk(self, document: NormalizedDocument, config: ChunkingConfig) -> ChunkingResult: ...
