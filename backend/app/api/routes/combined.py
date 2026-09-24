"""KrishiSetu AI - Combined Analysis Routes.

POST /api/v1/analyze

Combines leaf-image disease prediction, weather lookup via farm coordinates,
and rule-based risk analysis into a single call.
"""

import logging
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from PIL import Image

from app.core.config import get_settings
from app.models.schemas import CombinedAnalysisResponse, ErrorResponse
from app.services.combined_service import get_combined_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=CombinedAnalysisResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_413_CONTENT_TOO_LARGE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
    summary="Combined disease + weather + risk analysis",
    description=(
        "Upload a leaf image together with farm coordinates to run disease "
        "prediction, fetch nearby weather from Open-Meteo, and evaluate an "
        "agricultural outbreak risk score — all in a single response. "
        "Accepts multipart/form-data with fields: image, latitude, longitude."
    ),
)
async def analyze_combined(
    image: UploadFile = File(..., description="Leaf image file (JPEG, PNG, or WEBP)"),
    latitude: float = Form(..., description="Farm latitude in decimal degrees (-90 to 90)"),
    longitude: float = Form(..., description="Farm longitude in decimal degrees (-180 to 180)"),
    combined_service=Depends(get_combined_service),
) -> CombinedAnalysisResponse:
    """Run disease prediction, weather lookup, and risk analysis in one call."""
    settings = get_settings()

    # ---------------------------------------------------------------
    # Model availability check
    # ---------------------------------------------------------------
    model_service = combined_service.model_service
    if not model_service.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Disease model not loaded: {model_service.get_load_error()}",
        )

    # ---------------------------------------------------------------
    # Coordinate validation
    # ---------------------------------------------------------------
    if not (-90.0 <= latitude <= 90.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid latitude: {latitude}. Must be between -90 and 90.",
        )

    if not (-180.0 <= longitude <= 180.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid longitude: {longitude}. Must be between -180 and 180.",
        )

    # ---------------------------------------------------------------
    # Image validation (same rules as /api/v1/predict)
    # ---------------------------------------------------------------
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type and image.content_type.lower() not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {image.content_type}. Supported: JPEG, PNG, WEBP",
        )

    try:
        raw_data = await image.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read image file: {str(e)}",
        )

    # Size guard
    if len(raw_data) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Uploaded file exceeds the {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB size limit.",
        )

    try:
        pil_image = Image.open(BytesIO(raw_data))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}",
        )

    # ---------------------------------------------------------------
    # Run the combined disease -> weather -> risk pipeline
    # ---------------------------------------------------------------
    try:
        return await combined_service.analyze(pil_image, latitude, longitude)
    except ValueError as e:
        # Invalid image (corrupted, unsupported format, invalid coords)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        # Weather API timeout / network issues -> 503; other runtime -> 500
        message = str(e)
        if "Unable to reach" in message or "timed out" in message:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=message,
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in combined analysis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during combined analysis.",
        )
