export interface DiseasePrediction {
  crop: string;
  disease: string;
  confidence: number;
  class_name: string;
}

export interface WeatherHourlyPoint {
  timestamp: string;
  temperature_c?: number | null;
  relative_humidity_percent?: number | null;
  precipitation_mm?: number | null;
  precipitation_probability_percent?: number | null;
  wind_speed_kmh?: number | null;
  wind_direction_deg?: number | null;
}

export interface WeatherForecastResponse {
  latitude: number;
  longitude: number;
  timezone: string;
  timezone_abbreviation: string;
  elevation_m?: number | null;
  hourly: WeatherHourlyPoint[];
  retrieved_at: string;
}

export interface RiskFactor {
  factor: string;
  description: string;
  points: number;
}

export interface RiskAnalysisResponse {
  risk_level: string;
  risk_score: number;
  contributing_factors: RiskFactor[];
  recommendation: string;
  disclaimer: string;
}

export interface LocationInfo {
  latitude: number;
  longitude: number;
}

export interface CombinedAnalysisResponse {
  prediction: DiseasePrediction;
  low_confidence: boolean;
  confidence_threshold: number;
  message: string;
  model_info: Record<string, unknown>;
  weather: WeatherForecastResponse;
  risk: RiskAnalysisResponse;
  location: LocationInfo;
}

export interface ApiError {
  detail: string;
  error_code?: string | null;
  status_code?: number;
}
