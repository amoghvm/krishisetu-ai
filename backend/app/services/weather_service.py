"""KrishiSetu AI - Weather Service (Open-Meteo).

Retrieves real-time forecast data from the Open-Meteo API using httpx.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class WeatherService:
    """Async weather service backed by the Open-Meteo forecast API."""

    def __init__(self):
        self.settings = get_settings()
        self._base_url = self.settings.WEATHER_BASE_URL
        self._timeout = self.settings.WEATHER_REQUEST_TIMEOUT_SECONDS

    def _validate_coordinates(self, latitude: float, longitude: float) -> None:
        """Validate latitude and longitude are within valid ranges."""
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")

    async def fetch_forecast(
        self,
        latitude: float,
        longitude: float,
        hourly_vars: Optional[List[str]] = None,
    ) -> Dict:
        """Fetch normalized forecast data from Open-Meteo."""
        self._validate_coordinates(latitude, longitude)

        if hourly_vars is None:
            hourly_vars = [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "precipitation_probability",
                "wind_speed_10m",
                "wind_direction_10m",
            ]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(hourly_vars),
            "timezone": "auto",
            "forecast_days": 3,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(self._base_url, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as e:
            logger.error(f"Weather API timeout: {e}")
            raise RuntimeError("Weather service timed out. Please try again later.") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Weather API HTTP error {e.response.status_code}: {e}")
            raise RuntimeError(f"Weather service returned error {e.response.status_code}.") from e
        except httpx.RequestError as e:
            logger.error(f"Weather API request error: {e}")
            raise RuntimeError("Unable to reach weather service. Check your connection.") from e

        return self._normalize(latitude, longitude, data)

    def _normalize(self, latitude: float, longitude: float, raw: Dict) -> Dict:
        """Convert raw Open-Meteo response into a clean normalized structure."""
        hourly = raw.get("hourly", {})
        times = hourly.get("time", [])

        entries = []
        for i, ts in enumerate(times):
            entry = {
                "timestamp": ts,
                "temperature_c": hourly.get("temperature_2m", [None] * len(times))[i],
                "relative_humidity_percent": hourly.get("relative_humidity_2m", [None] * len(times))[i],
                "precipitation_mm": hourly.get("precipitation", [None] * len(times))[i],
                "precipitation_probability_percent": hourly.get("precipitation_probability", [None] * len(times))[i],
                "wind_speed_kmh": hourly.get("wind_speed_10m", [None] * len(times))[i],
                "wind_direction_deg": hourly.get("wind_direction_10m", [None] * len(times))[i],
            }
            entries.append(entry)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": raw.get("timezone", "UTC"),
            "timezone_abbreviation": raw.get("timezone_abbreviation", "UTC"),
            "elevation_m": raw.get("elevation"),
            "hourly": entries,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }


# Global service instance
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Get or create the global weather service instance."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service