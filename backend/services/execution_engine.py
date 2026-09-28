from datetime import datetime


def execute_action_plan(
    purchase_order_id,
    action_plan,
):
    if not action_plan.get("human_review_required"):
        return {
            "purchase_order_id": purchase_order_id,
            "execution_status": "EXECUTED",
            "message": "No human approval was required.",
            "executed_actions": [],
        }

    executed_actions = []

    for action in action_plan.get("actions", []):
        executed_actions.append(
            {
                "action_id": action["action_id"],
                "action": action["action"],
                "status": "COMPLETED",
                "completed_at": datetime.utcnow().isoformat(),
            }
        )

    return {
        "purchase_order_id": purchase_order_id,
        "execution_status": "EXECUTED",
        "message": (
            "Action plan executed successfully "
            "after human approval."
        ),
        "executed_actions": executed_actions,
        "executed_at": datetime.utcnow().isoformat(),
    }