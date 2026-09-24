"""KrishiSetu AI - Health Check Routes."""

from fastapi import APIRouter, Depends

from app.models.schemas import HealthResponse
from app.services.model_service import get_model_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(model_service=Depends(get_model_service)) -> HealthResponse:
    """
    Health check endpoint.

    Returns the API status and whether the disease model is loaded.
    """
    model_loaded = model_service.is_loaded()
    model_info = None

    if model_loaded:
        model_info = model_service.get_model_info()
    else:
        model_info = {"error": model_service.get_load_error()}

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        service="KrishiSetu AI Backend",
        version="1.0.0",
        model_loaded=model_loaded,
        model_info=model_info,
    )