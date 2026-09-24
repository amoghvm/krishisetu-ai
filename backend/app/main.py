"""KrishiSetu AI - FastAPI Application Entry Point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import combined, disease, health, risk, weather
from app.core.config import get_settings
from app.services.model_service import get_model_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    settings = get_settings()
    logger.info("Starting KrishiSetu AI Backend...")

    # Load disease model on startup
    model_service = get_model_service()
    success = model_service.load_model()

    if success:
        logger.info("Disease model loaded successfully")
    else:
        error = model_service.get_load_error()
        logger.error(f"Failed to load disease model: {error}")

    yield

    # Shutdown
    logger.info("Shutting down KrishiSetu AI Backend...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="KrishiSetu AI API",
        description="Crop Disease Identification & Early Outbreak Risk Advisory API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(disease.router, prefix="/api/v1", tags=["Disease Prediction"])
    app.include_router(weather.router, prefix="/api/v1", tags=["Weather"])
    app.include_router(risk.router, prefix="/api/v1", tags=["Risk Analysis"])
    app.include_router(combined.router, prefix="/api/v1", tags=["Combined Analysis"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )