"""KrishiSetu AI - Rule-Based Agricultural Risk Analysis Service."""

from app.models.schemas import RiskAnalysisRequest, RiskAnalysisResponse, RiskFactor


class RiskService:
    """Deterministic rule-based prototype for agricultural risk assessment."""

    DISCLAIMER = (
        "This is a prototype rule-based risk assessment based on the provided "
        "disease and weather inputs. It is not a scientifically validated "
        "pest migration prediction model and should not be used as the sole "
        "basis for pesticide or agricultural decisions."
    )

    def analyze(self, request: RiskAnalysisRequest) -> RiskAnalysisResponse:
        """Calculate a risk score from disease and weather factors."""

        score = 0.0
        factors: list[RiskFactor] = []

        # ------------------------------------------------------------------
        # Disease factor
        # ------------------------------------------------------------------
        if request.confidence is not None:
            if request.confidence >= 0.60:
                points = 30.0
                description = (
                    f"Disease detected with {request.confidence * 100:.1f}% confidence."
                )
            else:
                points = 15.0
                description = (
                    f"Disease prediction has low confidence "
                    f"({request.confidence * 100:.1f}%)."
                )

            score += points
            factors.append(
                RiskFactor(
                    factor="disease_detection",
                    description=description,
                    points=points,
                )
            )

        # ------------------------------------------------------------------
        # Temperature factor
        # ------------------------------------------------------------------
        if request.temperature_c is not None:
            if 20.0 <= request.temperature_c <= 30.0:
                points = 15.0
                score += points

                factors.append(
                    RiskFactor(
                        factor="temperature",
                        description=(
                            f"Temperature of {request.temperature_c:.1f}°C "
                            "falls within the prototype elevated-risk range."
                        ),
                        points=points,
                    )
                )

            elif request.temperature_c > 30.0:
                points = 10.0
                score += points

                factors.append(
                    RiskFactor(
                        factor="high_temperature",
                        description=(
                            f"High temperature of {request.temperature_c:.1f}°C "
                            "contributes to the prototype risk score."
                        ),
                        points=points,
                    )
                )

        # ------------------------------------------------------------------
        # Humidity factor
        # ------------------------------------------------------------------
        if request.relative_humidity_percent is not None:
            if request.relative_humidity_percent > 80.0:
                points = 15.0
                score += points

                factors.append(
                    RiskFactor(
                        factor="high_humidity",
                        description=(
                            f"Relative humidity of "
                            f"{request.relative_humidity_percent:.1f}% "
                            "is above 80%."
                        ),
                        points=points,
                    )
                )

            if request.relative_humidity_percent > 90.0:
                points = 10.0
                score += points

                factors.append(
                    RiskFactor(
                        factor="very_high_humidity",
                        description=(
                            f"Relative humidity of "
                            f"{request.relative_humidity_percent:.1f}% "
                            "is above 90%."
                        ),
                        points=points,
                    )
                )

        # ------------------------------------------------------------------
        # Precipitation probability
        # ------------------------------------------------------------------
        if request.precipitation_probability_percent is not None:
            if request.precipitation_probability_percent > 70.0:
                points = 10.0
                score += points

                factors.append(
                    RiskFactor(
                        factor="precipitation_probability",
                        description=(
                            f"Precipitation probability of "
                            f"{request.precipitation_probability_percent:.1f}% "
                            "is above 70%."
                        ),
                        points=points,
                    )
                )

        # ------------------------------------------------------------------
        # Precipitation amount
        # ------------------------------------------------------------------
        if request.precipitation_mm is not None:
            if request.precipitation_mm > 5.0:
                points = 10.0
                score += points

                factors.append(
                    RiskFactor(
                        factor="precipitation",
                        description=(
                            f"Precipitation of {request.precipitation_mm:.1f} mm "
                            "is above 5 mm."
                        ),
                        points=points,
                    )
                )

        # ------------------------------------------------------------------
        # Wind factor
        # ------------------------------------------------------------------
        if request.wind_speed_kmh is not None:
            if request.wind_speed_kmh > 30.0:
                points = 10.0
                score += points

                factors.append(
                    RiskFactor(
                        factor="high_wind",
                        description=(
                            f"Wind speed of {request.wind_speed_kmh:.1f} km/h "
                            "is above 30 km/h."
                        ),
                        points=points,
                    )
                )

        # Safety clamp
        score = min(max(score, 0.0), 100.0)

        # ------------------------------------------------------------------
        # Risk category
        # ------------------------------------------------------------------
        if score <= 25:
            risk_level = "low"
            recommendation = (
                "Continue routine crop monitoring. No immediate additional "
                "action is suggested by this prototype assessment."
            )

        elif score <= 50:
            risk_level = "moderate"
            recommendation = (
                "Increase field monitoring and inspect affected plants "
                "regularly. Consider preventive agricultural practices."
            )

        elif score <= 75:
            risk_level = "high"
            recommendation = (
                "Increase monitoring frequency and inspect the crop carefully "
                "for disease or pest symptoms. Consider consulting local "
                "agricultural guidance before taking control measures."
            )

        else:
            risk_level = "critical"
            recommendation = (
                "Perform prompt field inspection and seek local agricultural "
                "expert guidance before applying any pesticide or treatment."
            )

        return RiskAnalysisResponse(
            risk_level=risk_level,
            risk_score=round(score, 2),
            contributing_factors=factors,
            recommendation=recommendation,
            disclaimer=self.DISCLAIMER,
        )


# Singleton service instance
_risk_service = RiskService()


def get_risk_service() -> RiskService:
    """Return the shared risk service instance."""
    return _risk_service