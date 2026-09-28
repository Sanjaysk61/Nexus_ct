def generate_action_plan(root_cause_result):
    risk_level = root_cause_result["risk_level"]
    recommended_action = root_cause_result["recommended_action"]
    approval_route = root_cause_result["approval_route"]
    human_review_required = root_cause_result["human_review_required"]

    root_causes = root_cause_result["root_causes"]

    actions = []

    if risk_level == "HIGH":
        actions.append(
            {
                "action_id": "ACT-001",
                "action": "VALIDATE_PURCHASE_ORDER",
                "description": (
                    "Validate the purchase order value, scope "
                    "and supporting procurement documentation."
                ),
                "priority": "HIGH",
            }
        )

        actions.append(
            {
                "action_id": "ACT-002",
                "action": "VERIFY_APPROVAL_AUTHORITY",
                "description": (
                    "Verify that the required approval authority "
                    "is available for this procurement transaction."
                ),
                "priority": "HIGH",
            }
        )

        actions.append(
            {
                "action_id": "ACT-003",
                "action": "REVIEW_ROOT_CAUSES",
                "description": (
                    "Review the identified procurement risk drivers "
                    "before allowing the transaction to proceed."
                ),
                "priority": "HIGH",
            }
        )

    elif risk_level == "MEDIUM":
        actions.append(
            {
                "action_id": "ACT-001",
                "action": "PERFORM_MANUAL_REVIEW",
                "description": (
                    "Perform a manual review of the procurement "
                    "assessment and identified risk factors."
                ),
                "priority": "MEDIUM",
            }
        )

        actions.append(
            {
                "action_id": "ACT-002",
                "action": "VERIFY_PROCUREMENT_DOCUMENTATION",
                "description": (
                    "Verify the supporting procurement documentation "
                    "before proceeding."
                ),
                "priority": "MEDIUM",
            }
        )

    else:
        actions.append(
            {
                "action_id": "ACT-001",
                "action": "PROCEED_WITH_STANDARD_CONTROL",
                "description": (
                    "Proceed using the standard procurement "
                    "control process."
                ),
                "priority": "LOW",
            }
        )

    if human_review_required:
        execution_status = "PENDING_HUMAN_APPROVAL"
    else:
        execution_status = "READY_FOR_STANDARD_PROCESS"

    return {
        "purchase_order_id": root_cause_result[
            "purchase_order_id"
        ],
        "requisition_id": root_cause_result[
            "requisition_id"
        ],
        "supplier_id": root_cause_result[
            "supplier_id"
        ],
        "supplier_name": root_cause_result[
            "supplier_name"
        ],
        "risk_level": risk_level,
        "complexity": root_cause_result[
            "complexity"
        ],
        "approval_route": approval_route,
        "recommended_action": recommended_action,
        "human_review_required": human_review_required,
        "execution_status": execution_status,
        "root_causes": root_causes,
        "actions": actions,
    }