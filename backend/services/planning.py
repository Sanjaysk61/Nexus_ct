def generate_action_plan(root_cause_result):
    purchase_order_id = root_cause_result["purchase_order_id"]
    supplier_name = root_cause_result["supplier_name"]
    risk_level = root_cause_result["risk_level"]
    complexity = root_cause_result["complexity"]
    purchase_order_value = root_cause_result["purchase_order_value"]
    approval_route = root_cause_result["approval_route"]
    recommendation = root_cause_result["recommendation"]
    human_review_required = root_cause_result["human_review_required"]
    root_causes = root_cause_result["root_causes"]

    actions = []

    if risk_level == "HIGH":
        actions.append(
            {
                "action_id": "ACT-001",
                "action": "Perform human risk review",
                "priority": "HIGH",
                "reason": (
                    "The procurement transaction is classified "
                    "as HIGH risk."
                ),
                "requires_approval": True,
            }
        )

    if complexity == "HIGH_COMPLEXITY":
        actions.append(
            {
                "action_id": "ACT-002",
                "action": "Validate high-value procurement justification",
                "priority": "HIGH",
                "reason": (
                    "The purchase order falls within the "
                    "highest procurement complexity tier."
                ),
                "requires_approval": True,
            }
        )

    if approval_route == "ESCALATION":
        actions.append(
            {
                "action_id": "ACT-003",
                "action": "Route purchase order through escalation workflow",
                "priority": "HIGH",
                "reason": (
                    "The procurement engine assigned the "
                    "ESCALATION approval route."
                ),
                "requires_approval": True,
            }
        )

    if human_review_required:
        actions.append(
            {
                "action_id": "ACT-004",
                "action": "Obtain human approval before execution",
                "priority": "HIGH",
                "reason": (
                    "The deterministic assessment requires "
                    "human review."
                ),
                "requires_approval": True,
            }
        )

    if not actions:
        actions.append(
            {
                "action_id": "ACT-001",
                "action": "Proceed with standard procurement workflow",
                "priority": "NORMAL",
                "reason": (
                    "No elevated procurement action was "
                    "identified."
                ),
                "requires_approval": False,
            }
        )

    return {
        "purchase_order_id": purchase_order_id,
        "supplier_name": supplier_name,
        "purchase_order_value": purchase_order_value,
        "risk_level": risk_level,
        "complexity": complexity,
        "approval_route": approval_route,
        "recommendation": recommendation,
        "human_review_required": human_review_required,
        "root_cause_count": len(root_causes),
        "actions": actions,
        "action_count": len(actions),
        "execution_status": "PENDING_HUMAN_APPROVAL"
        if human_review_required
        else "READY_FOR_EXECUTION",
    }