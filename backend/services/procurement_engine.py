def analyze_purchase_order(
    purchase_order,
    supplier,
    requisition,
):
    amount = float(purchase_order.total_amount)
    reliability = float(supplier.reliability_score or 0)

    if amount <= 50000:
        complexity = "SIMPLE"
        approval_route = "AUTO_APPROVAL"
    elif amount <= 250000:
        complexity = "MODERATE"
        approval_route = "MANAGER_APPROVAL"
    elif amount <= 500000:
        complexity = "COMPLEX"
        approval_route = "EXECUTIVE_APPROVAL"
    else:
        complexity = "HIGH_COMPLEXITY"
        approval_route = "ESCALATION"

    if reliability < 0.70:
        supplier_risk = "HIGH"
    elif reliability < 0.85:
        supplier_risk = "MEDIUM"
    else:
        supplier_risk = "LOW"

    if complexity == "HIGH_COMPLEXITY":
        risk_level = "HIGH"
    elif supplier_risk == "HIGH":
        risk_level = "HIGH"
    elif complexity == "COMPLEX" or supplier_risk == "MEDIUM":
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if risk_level == "HIGH":
        recommendation = "REVIEW_REQUIRED"
    elif risk_level == "MEDIUM":
        recommendation = "MANUAL_REVIEW"
    else:
        recommendation = "PROCEED"

    explanation = (
        f"Purchase order value is INR {amount:,.2f}. "
        f"The procurement complexity is {complexity}. "
        f"The supplier reliability score is {reliability:.2f}, "
        f"resulting in {supplier_risk} supplier risk. "
        f"The recommended approval route is {approval_route}."
    )

    return {
        "purchase_order_id": purchase_order.purchase_order_id,
        "requisition_id": requisition.requisition_id,
        "supplier_id": supplier.supplier_id,
        "supplier_name": supplier.supplier_name,
        "purchase_order_value": amount,
        "currency": purchase_order.currency,
        "supplier_reliability_score": reliability,
        "complexity": complexity,
        "supplier_risk": supplier_risk,
        "risk_level": risk_level,
        "approval_route": approval_route,
        "recommendation": recommendation,
        "explanation": explanation,
    }