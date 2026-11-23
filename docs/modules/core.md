# Core module

## Responsibility and implementation

The core module contains cross-cutting configuration, contracts, provider
protocols, exceptions, and logging. It does not own document extraction or provider
implementations.

- [`app/core/config/settings.py`](../../app/core/config/settings.py) defines
  environment-backed settings using Pydantic Settings. `get_settings()` is cached.
  Defaults include a 50 MiB upload cap, disabled LLM enrichment, hash embeddings,
  and in-memory vectors. The allowed MIME types default to PDF, plain text,
  Markdown, PNG, JPEG, and TIFF.
- [`app/core/models/contracts.py`](../../app/core/models/contracts.py) defines
  document metadata and ingestion state/status models using Pydantic and `StrEnum`.
- [`app/core/interfaces/providers.py`](../../app/core/interfaces/providers.py)
  defines `Protocol` boundaries for object storage, document metadata, and jobs.
- [`app/core/exceptions/errors.py`](../../app/core/exceptions/errors.py) defines
  application-level ingestion exceptions.
- [`app/core/logging/setup.py`](../../app/core/logging/setup.py) configures
  standard-library logging to stdout.

## Libraries

**Pydantic**, **pydantic-settings**, and Python's `typing.Protocol`, `enum`,
`logging`, and `datetime` are the main tools.

## Alternatives

Protocols are lightweight structural interfaces and fit this modular monolith.
Abstract base classes may be useful when implementations need shared behavior.
Settings can remain in Pydantic Settings or use another typed configuration
library, provided validation and environment-variable semantics stay explicit.

## Production enhancements

- Split settings by concern, validate provider combinations at startup, and fail
  clearly for invalid configuration rather than silently selecting defaults.
- Add secret management outside committed `.env` files.
- Add structured logs with correlation, document, and job identifiers; avoid
  logging document contents or credentials.
- Use explicit status transitions and append-only stage/error records for audit and
  retry tracking.
- Keep shared contracts stable and version API-facing schemas deliberately.
