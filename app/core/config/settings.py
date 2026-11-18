from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RAG Ingestion Engine"
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    document_max_bytes: int = Field(default=50 * 1024 * 1024, gt=0)
    llm_enabled: bool = False
    llm_provider: str = "disabled"
    llm_model: str = "llama3.2:3b"
    ollama_base_url: str = "http://127.0.0.1:11434"
    embedding_provider: str = "deterministic_hash"
    embedding_model: str = "deterministic-v1"
    embedding_dimension: int = 64
    vector_store_provider: str = "memory"
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "document_chunks"

    document_allowed_mime_types: set[str] = {
        "application/pdf",
        "text/plain",
        "text/markdown",
        "image/png",
        "image/jpeg",
        "image/tiff",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
