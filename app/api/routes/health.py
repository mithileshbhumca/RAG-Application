from fastapi import APIRouter, Depends

from app.api.schemas.responses import HealthResponse
from app.core.config.settings import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/api/v1/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
    )
