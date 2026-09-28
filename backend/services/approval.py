from datetime import datetime


def create_approval_request(action_plan):
    approval_required = action_plan["human_review_required"]

    if approval_required:
        status = "PENDING"
    else:
        status = "AUTO_APPROVED"

    return {
        "approval_id": f"APR-{action_plan['purchase_order_id']}",
        "purchase_order_id": action_plan["purchase_order_id"],
        "supplier_name": action_plan["supplier_name"],
        "purchase_order_value": action_plan["purchase_order_value"],
        "risk_level": action_plan["risk_level"],
        "complexity": action_plan["complexity"],
        "approval_route": action_plan["approval_route"],
        "recommendation": action_plan["recommendation"],
        "approval_required": approval_required,
        "status": status,
        "requested_at": datetime.utcnow().isoformat(),
        "reviewed_at": None,
        "reviewed_by": None,
        "review_comment": None,
    }


def process_approval(
    approval_request,
    decision,
    reviewer,
    comment=None,
):
    decision = decision.upper()

    if decision not in ["APPROVED", "REJECTED"]:
        raise ValueError(
            "Decision must be APPROVED or REJECTED."
        )

    approval_request["status"] = decision
    approval_request["reviewed_at"] = datetime.utcnow().isoformat()
    approval_request["reviewed_by"] = reviewer
    approval_request["review_comment"] = comment

    if decision == "APPROVED":
        approval_request["execution_status"] = (
            "READY_FOR_EXECUTION"
        )
    else:
        approval_request["execution_status"] = (
            "EXECUTION_BLOCKED"
        )

    return approval_request
