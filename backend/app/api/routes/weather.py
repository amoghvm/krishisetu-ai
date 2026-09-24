"""KrishiSetu AI - Weather Forecast Routes (Open-Meteo)."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.schemas import ErrorResponse, WeatherErrorResponse, WeatherForecastResponse
from app.services.weather_service import get_weather_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/weather",
    response_model=WeatherForecastResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": WeatherErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": WeatherErrorResponse},
    },
    summary="Get weather forecast",
    description=(
        "Retrieve a 3-hourly forecast from Open-Meteo for the given "
        "latitude and longitude. Returns temperature, humidity, precipitation, "
        "and wind data."
    ),
)
async def get_weather(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees"),
    weather_service=Depends(get_weather_service),
) -> WeatherForecastResponse:
    """Fetch normalized weather forecast for the given coordinates."""
    try:
        data = await weather_service.fetch_forecast(latitude=latitude, longitude=longitude)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        # Distinguish network failure (503) from server-side error (500)
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

    return WeatherForecastResponse(**data)