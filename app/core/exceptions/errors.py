class IngestionError(Exception):
    """Base exception for ingestion operations."""


class InvalidDocumentError(IngestionError):
    """Raised when an uploaded document is rejected by validation."""


class NotFoundError(IngestionError):
    """Raised when a requested document or resource does not exist."""


class ConflictError(IngestionError):
    """Raised when an operation conflicts with the current document state."""
