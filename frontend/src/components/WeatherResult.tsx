import React from 'react';
import type { WeatherForecastResponse, WeatherHourlyPoint } from '../api/types';

interface WeatherResultProps {
  weather: WeatherForecastResponse;
}

function getRiskLevel(tempC?: number | null): string {
  if (tempC === undefined || tempC === null) return 'N/A';
  return `${tempC.toFixed(1)}°C`;
}

function formatWind(dir?: number | null, speed?: number | null): string {
  if (dir === undefined || dir === null) {
    return speed !== undefined && speed !== null ? `${speed.toFixed(1)} km/h` : 'N/A';
  }
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const idx = Math.round(dir / 22.5) % 16;
  const arrow = ['↑', '↗', '↗', '↗', '→', '↘', '↘', '↘', '↓', '↙', '↙', '↙', '←', '↖', '↖', '↖'][idx];
  return speed !== undefined && speed !== null
    ? `${speed.toFixed(1)} km/h ${arrow} (${directions[idx]})`
    : `${arrow} N/A`;
}

export default function WeatherResult({ weather }: WeatherResultProps) {
  const currentPoint: WeatherHourlyPoint | undefined = weather.hourly?.[0];

  const row = (label: string, value: string) => (
    <div className="flex justify-between py-2 border-b border-earth-100 last:border-0">
      <span className="text-sm text-earth-500">{label}</span>
      <span className="text-sm font-medium text-earth-800">{value}</span>
    </div>
  );

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold text-earth-800 mb-4 flex items-center">
        <span className="mr-3 text-2xl">🌤️</span>
        Current Weather
      </h2>

      <div className="mb-3">
        <p className="text-sm text-earth-500">Location</p>
        <p className="text-sm font-medium text-earth-800">
          {weather.latitude.toFixed(4)}°, {weather.longitude.toFixed(4)}°
        </p>
        <p className="text-xs text-earth-400">
          {weather.timezone} ({weather.timezone_abbreviation})
        </p>
      </div>

      {currentPoint ? (
        <div>
          <p className="text-xs text-earth-400 mb-2">
            Near-term forecast ({currentPoint.timestamp})
          </p>
          {row('Temperature', getRiskLevel(currentPoint.temperature_c))}
          {row('Humidity', currentPoint.relative_humidity_percent !== null && currentPoint.relative_humidity_percent !== undefined
            ? `${currentPoint.relative_humidity_percent.toFixed(1)}%`
            : 'N/A')}
          {row('Precipitation', currentPoint.precipitation_mm !== null && currentPoint.precipitation_mm !== undefined
            ? `${currentPoint.precipitation_mm.toFixed(1)} mm`
            : 'N/A')}
          {row('Precip. Probability', currentPoint.precipitation_probability_percent !== null && currentPoint.precipitation_probability_percent !== undefined
            ? `${currentPoint.precipitation_probability_percent.toFixed(0)}%`
            : 'N/A')}
          {row('Wind', formatWind(currentPoint.wind_direction_deg, currentPoint.wind_speed_kmh))}
        </div>
      ) : (
        <p className="text-sm text-earth-500">No hourly forecast data available.</p>
      )}

      {weather.elevation_m !== null && weather.elevation_m !== undefined && (
        <p className="text-xs text-earth-400 mt-3">Elevation: {weather.elevation_m.toFixed(0)} m</p>
      )}
    </div>
  );
}
