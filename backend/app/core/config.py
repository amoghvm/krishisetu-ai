"""KrishiSetu AI - Configuration Management."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    PORT: int = Field(default=8000)
    HOST: str = Field(default="0.0.0.0")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173", "http://localhost:19006"])

    # Security
    SECRET_KEY: str = Field(default="change-this-insecure-key-to-a-random-32-byte-hex-string")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./backend/krishisetu.db")

    # Weather Service
    WEATHER_PROVIDER: str = Field(default="open-meteo")
    WEATHER_BASE_URL: str = Field(default="https://api.open-meteo.com/v1/forecast")
    WEATHER_CACHE_TTL_SECONDS: int = Field(default=3600)
    WEATHER_REQUEST_TIMEOUT_SECONDS: int = Field(default=10)
    WEATHER_API_KEY: Optional[str] = Field(default=None)

    # Machine Learning & Inference
    MODEL_WEIGHTS_PATH: str = Field(default="models/resnet18_plantvillage.pt")
    MODEL_CONFIDENCE_THRESHOLD: float = Field(default=0.60)
    INFERENCE_DEVICE: str = Field(default="cpu")

    # Multilingual & Voice
    DEFAULT_LANGUAGE: str = Field(default="en")
    TTS_PROVIDER: str = Field(default="browser_native")
    TTS_API_KEY: Optional[str] = Field(default=None)

    # Storage
    UPLOAD_DIR: str = Field(default="backend/uploads")
    MAX_UPLOAD_SIZE_BYTES: int = Field(default=10485760)  # 10 MB

    # Model Info (from metadata)
    MODEL_ARCHITECTURE: str = Field(default="ResNet18")
    MODEL_VERSION: str = Field(default="1.0.0")
    MODEL_NUM_CLASSES: int = Field(default=38)
    MODEL_INPUT_SIZE: List[int] = Field(default=[3, 224, 224])


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()