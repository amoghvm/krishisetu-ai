"""KrishiSetu AI - Disease Prediction Routes."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.models.schemas import (
    DiseasePrediction,
    ErrorResponse,
    PredictDiseaseResponse,
    SupportedFormatsResponse,
)
from app.services.model_service import get_model_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictDiseaseResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_413_CONTENT_TOO_LARGE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
    summary="Predict crop disease from image",
    description=(
        "Upload a leaf/crop image to classify the disease using the trained "
        "ResNet18 PlantVillage model. Supports JPEG, PNG, and WEBP formats."
    ),
)
async def predict_disease(
    file: UploadFile = File(..., description="Image file (JPEG, PNG, or WEBP)"),
    model_service=Depends(get_model_service),
) -> PredictDiseaseResponse:
    """Run disease inference on an uploaded image."""
    if not model_service.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Disease model not loaded: {model_service.get_load_error()}",
        )

    # Validate content type
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type and file.content_type.lower() not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {file.content_type}. Supported: JPEG, PNG, WEBP",
        )

    # Read and open image
    try:
        from PIL import Image
        from io import BytesIO

        data = await file.read()
        image = Image.open(BytesIO(data))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}",
        )

    # Run inference
    try:
        result = model_service.predict(image)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    prediction = DiseasePrediction(
        crop=result["crop"],
        disease=result["disease"],
        confidence=result["confidence"],
        class_name=result["class_name"],
    )

    threshold = result["threshold"]
    low_conf = result["low_confidence"]

    if low_conf:
        message = (
            f"Low confidence prediction ({result['confidence'] * 100:.1f}%). "
            f"Detected {result['crop']} - {result['disease']}. "
            "Please re-upload a clearer image or consult an agricultural officer."
        )
    else:
        message = (
            f"{result['crop']} - {result['disease']} detected with "
            f"{result['confidence'] * 100:.1f}% confidence"
        )

    return PredictDiseaseResponse(
        prediction=prediction,
        low_confidence=low_conf,
        confidence_threshold=threshold,
        message=message,
        model_info=model_service.get_model_info(),
    )


@router.get(
    "/formats",
    response_model=SupportedFormatsResponse,
    summary="List supported image formats",
    description="Returns the list of supported image formats and maximum upload size.",
)
async def supported_formats() -> SupportedFormatsResponse:
    """Return supported image formats and max upload size."""
    from app.core.config import get_settings

    settings = get_settings()
    return SupportedFormatsResponse(
        formats=["JPEG", "PNG", "WEBP"],
        max_size_mb=settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024),
    )