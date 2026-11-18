# Phase 6 Deployment

## Direct local execution

```bash
source .venv312/bin/activate
cp .env.example .env
uvicorn app.main:app --reload
```

The API listens on `127.0.0.1:8000` by default.

## Docker Compose

```bash
docker compose up --build
```

This starts the API and Qdrant. Persistent volumes are used for application metadata, documents, and Qdrant data.

The default deterministic embedding provider is suitable for local demonstration only. Configure `sentence_transformers` for semantic retrieval.
