from backend.services.procurement_engine import analyze_purchase_order




def generate_root_cause_analysis(
    purchase_order,
    supplier,
    requisition,
):
    assessment = analyze_purchase_order(
        purchase_order=purchase_order,
        supplier=supplier,
        requisition=requisition,
    )

    causes = []

    purchase_order_value = assessment["purchase_order_value"]
    complexity = assessment["complexity"]
    supplier_risk = assessment["supplier_risk"]
    reliability = assessment["supplier_reliability_score"]
    risk_level = assessment["risk_level"]

    if purchase_order_value > 500000:
        causes.append(
            {
                "factor": "HIGH_PURCHASE_ORDER_VALUE",
                "description": (
                    f"Purchase order value is INR "
                    f"{purchase_order_value:,.2f}, "
                    "which places the transaction in the "
                    "highest procurement complexity tier."
                ),
                "impact": "HIGH",
            }
        )

    if complexity == "HIGH_COMPLEXITY":
        causes.append(
            {
                "factor": "HIGH_PROCUREMENT_COMPLEXITY",
                "description": (
                    "The procurement transaction is classified "
                    "as HIGH_COMPLEXITY based on its purchase "
                    "order value."
                ),
                "impact": "HIGH",
            }
        )

    if supplier_risk == "HIGH":
        causes.append(
            {
                "factor": "SUPPLIER_RELIABILITY",
                "description": (
                    f"Supplier reliability is "
                    f"{reliability:.2f}, resulting in "
                    "HIGH supplier risk."
                ),
                "impact": "HIGH",
            }
        )

    elif supplier_risk == "MEDIUM":
        causes.append(
            {
                "factor": "SUPPLIER_RELIABILITY",
                "description": (
                    f"Supplier reliability is "
                    f"{reliability:.2f}, resulting in "
                    "MEDIUM supplier risk."
                ),
                "impact": "MEDIUM",
            }
        )

    if risk_level == "HIGH" and not causes:
        causes.append(
            {
                "factor": "OVERALL_PROCUREMENT_RISK",
                "description": (
                    "The procurement assessment has been "
                    "classified as HIGH risk."
                ),
                "impact": "HIGH",
            }
        )

    if risk_level == "HIGH":
        recommended_action = "ESCALATE_FOR_REVIEW"
    elif risk_level == "MEDIUM":
        recommended_action = "MANUAL_REVIEW"
    else:
        recommended_action = "PROCEED_WITH_STANDARD_CONTROL"

    return {
        "purchase_order_id": assessment["purchase_order_id"],
        "requisition_id": assessment["requisition_id"],
        "supplier_id": assessment["supplier_id"],
        "supplier_name": assessment["supplier_name"],
        "risk_level": risk_level,
        "complexity": complexity,
        "supplier_risk": supplier_risk,
        "supplier_reliability_score": reliability,
        "purchase_order_value": purchase_order_value,
        "approval_route": assessment["approval_route"],
        "recommendation": assessment["recommendation"],
        "root_causes": causes,
        "recommended_action": recommended_action,
        "human_review_required": risk_level in {
            "MEDIUM",
            "HIGH",
        },
    }

