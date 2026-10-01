from datetime import datetime, timedelta
from uuid import uuid4

from backend.database import SessionLocal
from backend.models import (
    ProcessEvent,
    PurchaseOrder,
    PurchaseRequisition,
    GoodsReceipt,
    Invoice,
    Payment,
)


def to_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    return datetime.combine(value, datetime.min.time())


def seed_process_events():
    db = SessionLocal()

    try:
        db.query(ProcessEvent).delete()

        purchase_orders = db.query(PurchaseOrder).all()

        created = 0

        for po in purchase_orders:
            po_id = po.purchase_order_id

            requisition = (
                db.query(PurchaseRequisition)
                .filter(
                    PurchaseRequisition.requisition_id
                    == po.requisition_id
                )
                .first()
            )

            goods_receipt = (
                db.query(GoodsReceipt)
                .filter(
                    GoodsReceipt.purchase_order_id
                    == po_id
                )
                .first()
            )

            invoice = (
                db.query(Invoice)
                .filter(
                    Invoice.purchase_order_id
                    == po_id
                )
                .first()
            )

            payment = None

            if invoice:
                payment = (
                    db.query(Payment)
                    .filter(
                        Payment.invoice_id
                        == invoice.invoice_id
                    )
                    .first()
                )

            po_time = to_datetime(po.order_date)

            if not po_time:
                po_time = datetime.now()

            pr_time = (
                to_datetime(requisition.created_at)
                if requisition
                else po_time - timedelta(days=2)
            )

            gr_time = (
                to_datetime(goods_receipt.receipt_date)
                if goods_receipt
                else po_time + timedelta(days=4)
            )

            invoice_time = (
                to_datetime(invoice.invoice_date)
                if invoice
                else gr_time + timedelta(days=1)
            )

            payment_time = (
                to_datetime(payment.payment_date)
                if payment
                else invoice_time + timedelta(days=3)
            )

            events = [
                (
                    "Purchase Requisition",
                    pr_time,
                    "EMP-001",
                ),
                (
                    "Approval",
                    pr_time + timedelta(days=1),
                    "APPROVER-001",
                ),
                (
                    "Purchase Order",
                    po_time,
                    "BUYER-001",
                ),
                (
                    "Supplier Confirmation",
                    po_time + timedelta(days=1),
                    po.supplier_id,
                ),
                (
                    "Goods Receipt",
                    gr_time,
                    "WAREHOUSE-001",
                ),
                (
                    "Invoice",
                    invoice_time,
                    po.supplier_id,
                ),
                (
                    "Invoice Verification",
                    invoice_time + timedelta(days=1),
                    "AP-001",
                ),
                (
                    "Payment",
                    payment_time,
                    "FINANCE-001",
                ),
            ]

            for activity, timestamp, resource_id in events:
                event = ProcessEvent(
                    event_id=str(uuid4()),
                    case_id=po_id,
                    activity=activity,
                    timestamp=timestamp,
                    resource_id=resource_id,
                    supplier_id=po.supplier_id,
                    purchase_order_id=po_id,
                    department_id=(
                        requisition.department
                        if requisition
                        else "PROCUREMENT"
                    ),
                    amount=float(po.total_amount or 0),
                )

                db.add(event)
                created += 1

        db.commit()

        print(f"Process events created: {created}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_process_events()