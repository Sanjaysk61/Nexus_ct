from datetime import datetime


audit_logs = []


def create_audit_log(
    purchase_order_id,
    event_type,
    status,
    actor,
    details=None,
):
    audit_entry = {
        "audit_id": f"AUD-{len(audit_logs) + 1:05d}",
        "purchase_order_id": purchase_order_id,
        "event_type": event_type,
        "status": status,
        "actor": actor,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat(),
    }

    audit_logs.append(audit_entry)

    return audit_entry


def get_audit_logs(purchase_order_id):
    return [
        log
        for log in audit_logs
        if log["purchase_order_id"]
        == purchase_order_id
    ]