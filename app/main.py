from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.exceptions import (
    ConflictError,
    IngestionError,
    InvalidDocumentError,
    NotFoundError,
)
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)
app.include_router(health_router)
app.include_router(documents_router)


@app.exception_handler(InvalidDocumentError)
async def invalid_document_handler(request: Request, exc: InvalidDocumentError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "InvalidDocumentError"},
    )


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc), "type": "NotFoundError"})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc), "type": "ConflictError"})


@app.exception_handler(IngestionError)
async def ingestion_error_handler(request: Request, exc: IngestionError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": exc.__class__.__name__},
    )
