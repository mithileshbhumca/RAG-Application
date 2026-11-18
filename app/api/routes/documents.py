import hashlib
import mimetypes
from pathlib import Path, PurePosixPath
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.api.dependencies import get_repository, get_storage
from app.api.schemas.responses import (
    DocumentMetadataResponse,
    DocumentStatusResponse,
    UploadResponse,
)
from app.core.config.settings import Settings, get_settings
from app.core.models.contracts import (
    DocumentMetadata,
    IngestionState,
    IngestionStatus,
)
from app.storage.local.filesystem import LocalFilesystemStorage
from app.storage.metadata.sqlite import SQLiteDocumentRepository

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile,
    settings: Settings = Depends(get_settings),
    storage: LocalFilesystemStorage = Depends(get_storage),
    repository: SQLiteDocumentRepository = Depends(get_repository),
) -> UploadResponse:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > settings.document_max_bytes:
        raise HTTPException(status_code=413, detail="Uploaded file exceeds configured size limit")

    media_type = file.content_type or mimetypes.guess_type(file.filename or "")[0]
    if not media_type or media_type not in settings.document_allowed_mime_types:
        raise HTTPException(status_code=415, detail="Unsupported document media type")

    checksum = hashlib.sha256(content).hexdigest()
    existing = await repository.find_by_checksum(checksum)
    if existing:
        return UploadResponse(document=existing, duplicate=True)

    document_id = f"doc_{uuid4().hex}"
    safe_name = PurePosixPath(file.filename or "upload").name
    key = f"{document_id}/original/{safe_name}"
    await storage.put(key, content, {"checksum_sha256": checksum, "source_name": safe_name})

    document = DocumentMetadata(
        document_id=document_id,
        source_file=key,
        media_type=media_type,
        byte_size=len(content),
        checksum_sha256=checksum,
        original_name=safe_name,
    )
    await repository.create_document(document)
    await repository.save_status(
        IngestionStatus(document_id=document_id, state=IngestionState.REGISTERED)
    )
    return UploadResponse(document=document, duplicate=False)


@router.post("/{document_id}/ingest", response_model=DocumentStatusResponse)
async def ingest_document(
    document_id: str,
    repository: SQLiteDocumentRepository = Depends(get_repository),
) -> DocumentStatusResponse:
    from app.api.dependencies import (
        get_analyzer,
        get_chunking_config,
        get_chunking_strategy,
        get_embedding_provider,
        get_knowledge_extractor,
        get_normalizer,
        get_processor_registry,
        get_vector_store,
    )
    from app.ingestion.orchestrator.orchestrator import IngestionOrchestrator

    orchestrator = IngestionOrchestrator(
        repository=repository,
        analyzer=get_analyzer(),
        registry=get_processor_registry(),
        normalizer=get_normalizer(),
        knowledge_extractor=get_knowledge_extractor(),
        chunking_strategy=get_chunking_strategy(),
        chunking_config=get_chunking_config(),
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
        storage_root=Path("./data/documents"),
    )
    try:
        status = await orchestrator.ingest(document_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Document not found") from exc
    return DocumentStatusResponse(status=status)


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_status(
    document_id: str,
    repository: SQLiteDocumentRepository = Depends(get_repository),
) -> DocumentStatusResponse:
    status = await repository.get_status(document_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentStatusResponse(status=status)


@router.get("/{document_id}/chunks")
async def get_chunks(
    document_id: str,
    repository: SQLiteDocumentRepository = Depends(get_repository),
):
    document = await repository.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id, "chunks": await repository.get_chunks(document_id)}


@router.get("/{document_id}/metadata", response_model=DocumentMetadataResponse)
async def get_metadata(
    document_id: str,
    repository: SQLiteDocumentRepository = Depends(get_repository),
) -> DocumentMetadataResponse:
    document = await repository.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentMetadataResponse(document=document)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    repository: SQLiteDocumentRepository = Depends(get_repository),
) -> None:
    document = await repository.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    await repository.delete_document(document_id)
    try:
        from app.api.dependencies import get_vector_store

        await get_vector_store().delete_document(document_id)
    except (AttributeError, NotImplementedError):
        pass
