from datetime import datetime

from sqlalchemy.orm import Session

from backend.models import (
    ApprovalDecision,
    PurchaseOrder,
)


VALID_DECISIONS = {
    "APPROVED",
    "REJECTED",
    "REQUEST_INFO",
}


def create_approval_decision(
    db: Session,
    purchase_order_id: str,
    decision: str,
    reviewer_id: str,
    comments: str | None = None,
):
    decision = decision.upper().strip()

    if decision not in VALID_DECISIONS:
        raise ValueError(
            "Invalid decision. "
            "Use APPROVED, REJECTED, or REQUEST_INFO."
        )

    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.purchase_order_id
            == purchase_order_id
        )
        .first()
    )

    if not purchase_order:
        raise ValueError(
            "Purchase order not found."
        )

    approval = ApprovalDecision(
        purchase_order_id=purchase_order_id,
        decision=decision,
        reviewer_id=reviewer_id,
        comments=comments,
        decided_at=datetime.utcnow(),
    )

    db.add(approval)

    if decision == "APPROVED":
        purchase_order.status = "APPROVED"

    elif decision == "REJECTED":
        purchase_order.status = "REJECTED"

    elif decision == "REQUEST_INFO":
        purchase_order.status = "PENDING_INFORMATION"

    db.commit()
    db.refresh(approval)

    return {
        "decision_id": approval.decision_id,
        "purchase_order_id": approval.purchase_order_id,
        "decision": approval.decision,
        "reviewer_id": approval.reviewer_id,
        "comments": approval.comments,
        "decided_at": approval.decided_at,
        "purchase_order_status": purchase_order.status,
    }


def get_approval_history(
    db: Session,
    purchase_order_id: str,
):
    purchase_order = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.purchase_order_id
            == purchase_order_id
        )
        .first()
    )

    if not purchase_order:
        raise ValueError(
            "Purchase order not found."
        )

    decisions = (
        db.query(ApprovalDecision)
        .filter(
            ApprovalDecision.purchase_order_id
            == purchase_order_id
        )
        .order_by(
            ApprovalDecision.decided_at.desc()
        )
        .all()
    )

    return {
        "purchase_order_id": purchase_order_id,
        "current_status": purchase_order.status,
        "approval_history": [
            {
                "decision_id": decision.decision_id,
                "decision": decision.decision,
                "reviewer_id": decision.reviewer_id,
                "comments": decision.comments,
                "decided_at": decision.decided_at,
            }
            for decision in decisions
        ],
    }