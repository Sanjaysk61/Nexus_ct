from typing import Any, Dict


def _to_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def simulate_scenario(
    base_data: Dict[str, Any],
    scenario: Dict[str, Any],
) -> Dict[str, Any]:

    base_value = _to_float(
        base_data.get("purchase_order_value")
    )

    base_reliability = _to_float(
        base_data.get(
            "supplier_reliability_score",
            1.0,
        ),
        1.0,
    )

    base_risk = str(
        base_data.get(
            "risk_level",
            "LOW",
        )
    ).upper()

    delay_days = _to_float(
        scenario.get("additional_delay_days")
    )

    reliability_change = _to_float(
        scenario.get(
            "supplier_reliability_change"
        )
    )

    value_change_percent = _to_float(
        scenario.get(
            "value_change_percent"
        )
    )

    simulated_value = (
        base_value
        * (
            1
            + value_change_percent / 100
        )
    )

    simulated_reliability = max(
        0.0,
        min(
            1.0,
            base_reliability
            + reliability_change,
        ),
    )

    risk_score = 0.20

    if simulated_value > 500000:
        risk_score += 0.25

    if simulated_value > 1000000:
        risk_score += 0.15

    if simulated_reliability < 0.70:
        risk_score += 0.25

    elif simulated_reliability < 0.85:
        risk_score += 0.10

    if base_risk == "HIGH":
        risk_score += 0.20

    elif base_risk == "MEDIUM":
        risk_score += 0.10

    if delay_days >= 7:
        risk_score += 0.20

    elif delay_days >= 3:
        risk_score += 0.10

    risk_score = min(
        1.0,
        round(
            risk_score,
            3,
        ),
    )

    if risk_score >= 0.70:
        simulated_risk = "HIGH"

    elif risk_score >= 0.40:
        simulated_risk = "MEDIUM"

    else:
        simulated_risk = "LOW"

    if delay_days >= 7:
        outcome = (
            "SIGNIFICANT_PROCESS_DELAY"
        )

    elif delay_days >= 3:
        outcome = (
            "POTENTIAL_PROCESS_DELAY"
        )

    elif simulated_risk == "HIGH":
        outcome = (
            "HIGH_RISK_TRANSACTION"
        )

    else:
        outcome = (
            "STANDARD_PROCESS_CONTINUATION"
        )

    if simulated_risk == "HIGH":
        recommendation = (
            "ESCALATE_FOR_REVIEW"
        )

    elif simulated_risk == "MEDIUM":
        recommendation = (
            "MONITOR_AND_REVIEW"
        )

    else:
        recommendation = (
            "PROCEED_WITH_STANDARD_CONTROL"
        )

    return {
        "scenario": scenario,
        "simulated_purchase_order_value": round(
            simulated_value,
            2,
        ),
        "simulated_supplier_reliability": round(
            simulated_reliability,
            3,
        ),
        "additional_delay_days": delay_days,
        "simulated_risk_score": risk_score,
        "simulated_risk_level": simulated_risk,
        "predicted_outcome": outcome,
        "recommended_action": recommendation,
    }


def generate_scenario_comparison(
    base_data: Dict[str, Any],
) -> Dict[str, Any]:

    scenarios = [
        {
            "scenario_id": "SCN-001",
            "name": "BASELINE",
            "additional_delay_days": 0,
            "supplier_reliability_change": 0,
            "value_change_percent": 0,
        },
        {
            "scenario_id": "SCN-002",
            "name": "SUPPLIER_DEGRADATION",
            "additional_delay_days": 3,
            "supplier_reliability_change": -0.20,
            "value_change_percent": 0,
        },
        {
            "scenario_id": "SCN-003",
            "name": "MAJOR_DELAY",
            "additional_delay_days": 7,
            "supplier_reliability_change": -0.10,
            "value_change_percent": 0,
        },
        {
            "scenario_id": "SCN-004",
            "name": "ORDER_VALUE_INCREASE",
            "additional_delay_days": 0,
            "supplier_reliability_change": 0,
            "value_change_percent": 20,
        },
    ]

    results = []

    for scenario in scenarios:
        result = simulate_scenario(
            base_data=base_data,
            scenario=scenario,
        )

        results.append(
            {
                "scenario_id": scenario[
                    "scenario_id"
                ],
                "scenario_name": scenario[
                    "name"
                ],
                "result": result,
            }
        )

    return {
        "purchase_order_id": base_data.get(
            "purchase_order_id"
        ),
        "baseline_risk": base_data.get(
            "risk_level"
        ),
        "scenarios": results,
    }