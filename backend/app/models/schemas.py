"""KrishiSetu AI - Pydantic Models for Disease Prediction."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DiseasePrediction(BaseModel):
    """Single disease prediction result."""

    crop: str = Field(..., description="Crop name")
    disease: str = Field(..., description="Disease/condition name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence score")
    class_name: str = Field(..., description="Raw class name from model")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "crop": "Tomato",
                "disease": "Late Blight",
                "confidence": 0.987,
                "class_name": "Tomato___Late_blight"
            }
        }
    )


class PredictDiseaseResponse(BaseModel):
    """Response for disease prediction endpoint."""

    prediction: DiseasePrediction
    low_confidence: bool = Field(..., description="Whether confidence is below threshold")
    confidence_threshold: float = Field(..., description="Configured confidence threshold")
    message: str = Field(..., description="Human-readable result message")
    model_info: dict = Field(..., description="Model version and metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prediction": {
                    "crop": "Tomato",
                    "disease": "Late Blight",
                    "confidence": 0.987,
                    "class_name": "Tomato___Late_blight"
                },
                "low_confidence": False,
                "confidence_threshold": 0.60,
                "message": "Tomato - Late Blight detected with 98.7% confidence",
                "model_info": {
                    "architecture": "ResNet18",
                    "version": "1.0.0",
                    "num_classes": 38
                }
            }
        }
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="API status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    model_loaded: bool = Field(..., description="Whether the disease model is loaded")
    model_info: Optional[dict] = Field(default=None, description="Model metadata if loaded")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "service": "KrishiSetu AI Backend",
                "version": "1.0.0",
                "model_loaded": True,
                "model_info": {
                    "architecture": "ResNet18",
                    "version": "1.0.0",
                    "num_classes": 38
                }
            }
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    error_code: Optional[str] = None
    status_code: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Invalid image file: Unsupported format. Supported formats: JPEG, PNG, WEBP",
                "error_code": "INVALID_IMAGE_FORMAT",
                "status_code": 400
            }
        }
    )


class SupportedFormatsResponse(BaseModel):
    """Supported image formats response."""

    formats: List[str] = Field(default=["JPEG", "PNG", "WEBP"])
    max_size_mb: int = Field(default=10)


# ==============================================================================
# Weather Schemas (Open-Meteo)
# ==============================================================================


class WeatherHourlyPoint(BaseModel):
    """A single hourly forecast data point."""

    timestamp: str = Field(..., description="ISO-8601 timestamp in local timezone")
    temperature_c: Optional[float] = Field(default=None, description="Temperature at 2m in °C")
    relative_humidity_percent: Optional[float] = Field(default=None, description="Relative humidity at 2m in %")
    precipitation_mm: Optional[float] = Field(default=None, description="Precipitation amount in mm")
    precipitation_probability_percent: Optional[float] = Field(default=None, description="Precipitation probability in %")
    wind_speed_kmh: Optional[float] = Field(default=None, description="Wind speed at 10m in km/h")
    wind_direction_deg: Optional[float] = Field(default=None, description="Wind direction at 10m in degrees")


class WeatherForecastResponse(BaseModel):
    """Normalized weather forecast response from Open-Meteo."""

    latitude: float = Field(..., description="Request latitude")
    longitude: float = Field(..., description="Request longitude")
    timezone: str = Field(default="UTC", description="Timezone name from API")
    timezone_abbreviation: str = Field(default="UTC", description="Timezone abbreviation")
    elevation_m: Optional[float] = Field(default=None, description="Elevation above sea level in meters")
    hourly: List[WeatherHourlyPoint] = Field(default_factory=list, description="Hourly forecast entries")
    retrieved_at: str = Field(..., description="ISO-8601 UTC retrieval timestamp")


class WeatherErrorResponse(BaseModel):
    """Error response for weather endpoints."""

    detail: str = Field(..., description="Human-readable error message")
    error_code: Optional[str] = Field(default=None, description="Machine-readable error code")


# ==============================================================================
# Risk Analysis Schemas (Rule-Based Prototype)
# ==============================================================================


class RiskFactor(BaseModel):
    """A single contributing factor to the risk score."""

    factor: str = Field(..., description="Short identifier for the factor")
    description: str = Field(..., description="Human-readable explanation")
    points: float = Field(..., description="Points contributed to the risk score")


class RiskAnalysisRequest(BaseModel):
    """Request body for the risk analysis endpoint."""

    disease: Optional[str] = Field(default=None, description="Detected disease/condition name")
    crop: Optional[str] = Field(default=None, description="Crop name")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Disease confidence score")
    temperature_c: Optional[float] = Field(default=None, description="Current/recent temperature in °C")
    relative_humidity_percent: Optional[float] = Field(default=None, description="Current/recent relative humidity in %")
    precipitation_mm: Optional[float] = Field(default=None, description="Recent or forecast precipitation in mm")
    precipitation_probability_percent: Optional[float] = Field(default=None, description="Precipitation probability in %")
    wind_speed_kmh: Optional[float] = Field(default=None, description="Wind speed in km/h")
    wind_direction_deg: Optional[float] = Field(default=None, description="Wind direction in degrees")


class RiskAnalysisResponse(BaseModel):
    """Structured risk analysis result from the rule-based engine."""

    risk_level: str = Field(..., description="Categorical risk level (low/moderate/high/critical)")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Aggregate risk score from 0 to 100")
    contributing_factors: List[RiskFactor] = Field(default_factory=list, description="Factors that influenced the score")
    recommendation: str = Field(..., description="Actionable, conservative recommendation")
    disclaimer: str = Field(..., description="Notice that this is a prototype rule-based assessment")


class RiskErrorResponse(BaseModel):
    """Error response for risk endpoints."""

    detail: str = Field(..., description="Human-readable error message")
    error_code: Optional[str] = Field(default=None, description="Machine-readable error code")


# ==============================================================================
# Combined Analysis Schemas
# ==============================================================================


class LocationInfo(BaseModel):
    """Geographic location context for a combined analysis."""

    latitude: float = Field(..., description="Request latitude")
    longitude: float = Field(..., description="Request longitude")


class CombinedAnalysisResponse(BaseModel):
    """Single combined response: disease prediction + weather + risk analysis."""

    prediction: DiseasePrediction = Field(..., description="Disease detection result")
    low_confidence: bool = Field(..., description="Whether the disease confidence is below threshold")
    confidence_threshold: float = Field(..., description="Configured disease confidence threshold")
    message: str = Field(..., description="Human-readable disease result message")
    model_info: dict = Field(..., description="Model version and metadata")
    weather: WeatherForecastResponse = Field(..., description="Normalized weather forecast from Open-Meteo")
    risk: RiskAnalysisResponse = Field(..., description="Rule-based risk assessment result")
    location: LocationInfo = Field(..., description="Farm location used for analysis")