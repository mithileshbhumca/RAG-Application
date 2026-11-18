# Phase 7 Validation

The baseline suite covers health, upload duplicate detection, plain-text ingestion, RAG chunk relationships, embeddings, knowledge extraction, API behavior, missing documents, and end-to-end text ingestion.

Run:

```bash
.venv312/bin/python -m ruff check app tests
.venv312/bin/python -m pytest -q
.venv312/bin/python -m pip check
```

Docker validation requires Docker Engine or Docker Desktop; it was not available during local validation.
