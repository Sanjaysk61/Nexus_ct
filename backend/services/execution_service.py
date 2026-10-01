from datetime import datetime


def execute_action_plan(
    purchase_order_id,
    action_plan,
):
    actions = action_plan.get("actions", [])

    executed_actions = []

    for action in actions:
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
        "execution_message": (
            "Procurement action plan executed "
            "after human approval."
        ),
        "executed_actions": executed_actions,
        "executed_at": datetime.utcnow().isoformat(),
    }