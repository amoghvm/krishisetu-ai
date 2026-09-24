"""KrishiSetu AI - Agricultural Risk Analysis Routes."""

import logging

from fastapi import APIRouter, Depends, status

from app.models.schemas import RiskAnalysisRequest, RiskAnalysisResponse, RiskErrorResponse
from app.services.risk_service import get_risk_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/risk/analyze",
    response_model=RiskAnalysisResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": RiskErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": RiskErrorResponse},
    },
    summary="Analyze agricultural outbreak risk",
    description=(
        "Evaluate a deterministic, rule-based agricultural risk score from disease "
        "detection confidence and weather factors. This is a prototype assessment "
        "and not a scientifically validated pest-migration prediction model."
    ),
)
async def analyze_risk(
    request: RiskAnalysisRequest,
    risk_service=Depends(get_risk_service),
) -> RiskAnalysisResponse:
    """Calculate an agricultural risk assessment from disease and weather inputs."""
    logger.info(
        "Risk analysis requested for crop=%s disease=%s",
        request.crop,
        request.disease,
    )
    return risk_service.analyze(request)
