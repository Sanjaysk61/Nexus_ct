from typing import Any, Dict


def _to_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def predict_procurement_risk(
    procurement_data: Dict[str, Any],
) -> Dict[str, Any]:

    purchase_order_value = _to_float(
        procurement_data.get(
            "purchase_order_value"
        )
    )

    supplier_reliability = _to_float(
        procurement_data.get(
            "supplier_reliability_score",
            1.0,
        ),
        1.0,
    )

    current_risk = str(
        procurement_data.get(
            "risk_level",
            "LOW",
        )
    ).upper()

    complexity = str(
        procurement_data.get(
            "complexity",
            "SIMPLE",
        )
    ).upper()

    supplier_risk = str(
        procurement_data.get(
            "supplier_risk",
            "LOW",
        )
    ).upper()

    risk_score = 0.0

    risk_factors = []

    if purchase_order_value > 500000:
        risk_score += 0.25

        risk_factors.append(
            "HIGH_PURCHASE_ORDER_VALUE"
        )

    if purchase_order_value > 1000000:
        risk_score += 0.15

        risk_factors.append(
            "VERY_HIGH_PURCHASE_ORDER_VALUE"
        )

    if complexity == "HIGH_COMPLEXITY":
        risk_score += 0.20

        risk_factors.append(
            "HIGH_PROCUREMENT_COMPLEXITY"
        )

    if supplier_risk == "HIGH":
        risk_score += 0.20

        risk_factors.append(
            "HIGH_SUPPLIER_RISK"
        )

    elif supplier_risk == "MEDIUM":
        risk_score += 0.10

        risk_factors.append(
            "MEDIUM_SUPPLIER_RISK"
        )

    if supplier_reliability < 0.70:
        risk_score += 0.15

        risk_factors.append(
            "LOW_SUPPLIER_RELIABILITY"
        )

    elif supplier_reliability < 0.85:
        risk_score += 0.05

        risk_factors.append(
            "MODERATE_SUPPLIER_RELIABILITY"
        )

    if current_risk == "HIGH":
        risk_score += 0.15

        risk_factors.append(
            "CURRENT_HIGH_RISK"
        )

    elif current_risk == "MEDIUM":
        risk_score += 0.08

        risk_factors.append(
            "CURRENT_MEDIUM_RISK"
        )

    risk_score = min(
        round(risk_score, 2),
        1.0,
    )

    if risk_score >= 0.70:
        predicted_risk = "HIGH"

    elif risk_score >= 0.40:
        predicted_risk = "MEDIUM"

    else:
        predicted_risk = "LOW"

    if predicted_risk == "HIGH":
        predicted_outcome = (
            "HIGH_PROBABILITY_OF_PROCUREMENT_ISSUE"
        )

        recommended_action = (
            "ESCALATE_AND_PERFORM_PREVENTIVE_REVIEW"
        )

    elif predicted_risk == "MEDIUM":
        predicted_outcome = (
            "POTENTIAL_PROCUREMENT_ISSUE"
        )

        recommended_action = (
            "MONITOR_TRANSACTION_AND_REVIEW"
        )

    else:
        predicted_outcome = (
            "NORMAL_PROCUREMENT_PROGRESS"
        )

        recommended_action = (
            "PROCEED_WITH_STANDARD_MONITORING"
        )

    return {
        "purchase_order_id": procurement_data.get(
            "purchase_order_id"
        ),
        "predicted_risk_score": risk_score,
        "predicted_risk_level": predicted_risk,
        "current_risk_level": current_risk,
        "predicted_outcome": predicted_outcome,
        "recommended_action": recommended_action,
        "risk_factors": risk_factors,
        "supplier_reliability_score": supplier_reliability,
        "purchase_order_value": purchase_order_value,
        "complexity": complexity,
        "supplier_risk": supplier_risk,
    }