"""KrishiSetu AI - Combined Analysis Service.

Orchestrates disease prediction -> weather lookup -> risk analysis,
reusing the existing ModelService, WeatherService, and RiskService
without duplicating their internal logic.
"""

import logging
from typing import Optional

from PIL import Image

from app.models.schemas import (
    CombinedAnalysisResponse,
    DiseasePrediction,
    LocationInfo,
    RiskAnalysisRequest,
    RiskAnalysisResponse,
    WeatherForecastResponse,
)
from app.services.model_service import DiseaseModelService, get_model_service
from app.services.risk_service import RiskService, get_risk_service
from app.services.weather_service import WeatherService, get_weather_service

logger = logging.getLogger(__name__)


class CombinedAnalysisService:
    """Coordinates disease, weather, and risk services into one analysis."""

    def __init__(self):
        self._model_service: Optional[DiseaseModelService] = None
        self._weather_service: Optional[WeatherService] = None
        self._risk_service: Optional[RiskService] = None

    @property
    def model_service(self) -> DiseaseModelService:
        if self._model_service is None:
            self._model_service = get_model_service()
        return self._model_service

    @property
    def weather_service(self) -> WeatherService:
        if self._weather_service is None:
            self._weather_service = get_weather_service()
        return self._weather_service

    @property
    def risk_service(self) -> RiskService:
        if self._risk_service is None:
            self._risk_service = get_risk_service()
        return self._risk_service

    def _select_current_point(self, hourly: list) -> Optional[dict]:
        """Return the nearest/near-term hourly forecast point (index 0)."""
        if not hourly:
            return None
        return hourly[0]

    async def analyze(
        self,
        image: Image.Image,
        latitude: float,
        longitude: float,
    ) -> CombinedAnalysisResponse:
        """Run the full disease -> weather -> risk pipeline.

        Args:
            image: A validated PIL Image (RGB-compatible) ready for inference.
            latitude: Farm latitude in decimal degrees.
            longitude: Farm longitude in decimal degrees.

        Returns:
            CombinedAnalysisResponse with prediction, weather, and risk data.
        """
        logger.info(
            "Combined analysis: lat=%s lon=%s", latitude, longitude
        )

        # ------------------------------------------------------------------
        # Step 1 - Disease prediction (reuse existing model service)
        # ------------------------------------------------------------------
        prediction_result = self.model_service.predict(image)

        prediction = DiseasePrediction(
            crop=prediction_result["crop"],
            disease=prediction_result["disease"],
            confidence=prediction_result["confidence"],
            class_name=prediction_result["class_name"],
        )

        # ------------------------------------------------------------------
        # Step 2 - Weather lookup (reuse existing weather service)
        # ------------------------------------------------------------------
        weather_data = await self.weather_service.fetch_forecast(
            latitude=latitude,
            longitude=longitude,
        )
        weather_response = WeatherForecastResponse(**weather_data)

        # ------------------------------------------------------------------
        # Step 3 - Select current/near-term weather point for risk engine
        # ------------------------------------------------------------------
        current_point = self._select_current_point(weather_response.hourly)

        risk_request = RiskAnalysisRequest(
            disease=prediction_result["disease"],
            crop=prediction_result["crop"],
            confidence=prediction_result["confidence"],
            temperature_c=getattr(current_point, "temperature_c", None) if current_point else None,
            relative_humidity_percent=getattr(current_point, "relative_humidity_percent", None) if current_point else None,
            precipitation_mm=getattr(current_point, "precipitation_mm", None) if current_point else None,
            precipitation_probability_percent=getattr(current_point, "precipitation_probability_percent", None) if current_point else None,
            wind_speed_kmh=getattr(current_point, "wind_speed_kmh", None) if current_point else None,
            wind_direction_deg=getattr(current_point, "wind_direction_deg", None) if current_point else None,
        )

        # ------------------------------------------------------------------
        # Step 4 - Risk analysis (reuse existing risk service)
        # ------------------------------------------------------------------
        risk_response: RiskAnalysisResponse = self.risk_service.analyze(risk_request)

        # ------------------------------------------------------------------
        # Step 5 - Assemble combined response
        # ------------------------------------------------------------------
        threshold = prediction_result["threshold"]
        low_conf = prediction_result["low_confidence"]

        if low_conf:
            message = (
                f"Low confidence prediction ({prediction_result['confidence'] * 100:.1f}%). "
                f"Detected {prediction_result['crop']} - {prediction_result['disease']}. "
                "Please re-upload a clearer image or consult an agricultural officer."
            )
        else:
            message = (
                f"{prediction_result['crop']} - {prediction_result['disease']} detected with "
                f"{prediction_result['confidence'] * 100:.1f}% confidence"
            )

        return CombinedAnalysisResponse(
            prediction=prediction,
            low_confidence=low_conf,
            confidence_threshold=threshold,
            message=message,
            model_info=self.model_service.get_model_info(),
            weather=weather_response,
            risk=risk_response,
            location=LocationInfo(
                latitude=latitude,
                longitude=longitude,
            ),
        )


# Singleton service instance
_combined_service: Optional[CombinedAnalysisService] = None


def get_combined_service() -> CombinedAnalysisService:
    """Return the shared combined analysis service instance."""
    global _combined_service
    if _combined_service is None:
        _combined_service = CombinedAnalysisService()
    return _combined_service
