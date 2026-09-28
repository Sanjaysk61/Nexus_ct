from sqlalchemy.orm import Session

from backend.models import (
    Supplier,
    Product,
    PurchaseRequisition,
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceipt,
    Invoice,
    Payment,
)
from backend.services.procurement_engine import analyze_purchase_order


def generate_process_intelligence(db: Session):
    suppliers = db.query(Supplier).all()
    products = db.query(Product).all()
    requisitions = db.query(PurchaseRequisition).all()
    purchase_orders = db.query(PurchaseOrder).all()
    purchase_order_items = db.query(PurchaseOrderItem).all()
    goods_receipts = db.query(GoodsReceipt).all()
    invoices = db.query(Invoice).all()
    payments = db.query(Payment).all()

    total_supplier_count = len(suppliers)
    total_product_count = len(products)
    total_requisition_count = len(requisitions)
    total_po_count = len(purchase_orders)
    total_receipt_count = len(goods_receipts)
    total_invoice_count = len(invoices)
    total_payment_count = len(payments)

    total_po_value = sum(
        float(po.total_amount or 0)
        for po in purchase_orders
    )

    total_payment_value = sum(
        float(payment.payment_amount or 0)
        for payment in payments
    )

    average_po_value = (
        total_po_value / total_po_count
        if total_po_count
        else 0
    )

    supplier_reliability = [
        float(supplier.reliability_score or 0)
        for supplier in suppliers
    ]

    average_supplier_reliability = (
        sum(supplier_reliability)
        / len(supplier_reliability)
        if supplier_reliability
        else 0
    )

    high_risk_suppliers = [
        supplier
        for supplier in suppliers
        if float(supplier.reliability_score or 0) < 0.70
    ]

    medium_risk_suppliers = [
        supplier
        for supplier in suppliers
        if 0.70 <= float(supplier.reliability_score or 0) < 0.85
    ]

    reliable_suppliers = [
        supplier
        for supplier in suppliers
        if float(supplier.reliability_score or 0) >= 0.85
    ]

    complexity_distribution = {
        "SIMPLE": 0,
        "MODERATE": 0,
        "COMPLEX": 0,
        "HIGH_COMPLEXITY": 0,
    }

    risk_distribution = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
    }

    approval_route_distribution = {
        "AUTO_APPROVAL": 0,
        "MANAGER_APPROVAL": 0,
        "EXECUTIVE_APPROVAL": 0,
        "ESCALATION": 0,
    }

    procurement_assessments = []

    supplier_lookup = {
        supplier.supplier_id: supplier
        for supplier in suppliers
    }

    requisition_lookup = {
        requisition.requisition_id: requisition
        for requisition in requisitions
    }

    for purchase_order in purchase_orders:
        supplier = supplier_lookup.get(
            purchase_order.supplier_id
        )

        requisition = requisition_lookup.get(
            purchase_order.requisition_id
        )

        if not supplier or not requisition:
            continue

        assessment = analyze_purchase_order(
            purchase_order=purchase_order,
            supplier=supplier,
            requisition=requisition,
        )

        complexity = assessment["complexity"]
        risk_level = assessment["risk_level"]
        approval_route = assessment["approval_route"]

        if complexity in complexity_distribution:
            complexity_distribution[complexity] += 1

        if risk_level in risk_distribution:
            risk_distribution[risk_level] += 1

        if approval_route in approval_route_distribution:
            approval_route_distribution[
                approval_route
            ] += 1

        procurement_assessments.append(assessment)

    high_value_orders = sorted(
        procurement_assessments,
        key=lambda item: item["purchase_order_value"],
        reverse=True,
    )[:5]

    supplier_po_value = {}

    for purchase_order in purchase_orders:
        supplier_id = purchase_order.supplier_id

        supplier_po_value[supplier_id] = (
            supplier_po_value.get(supplier_id, 0)
            + float(purchase_order.total_amount or 0)
        )

    supplier_spend = []

    for supplier in suppliers:
        value = supplier_po_value.get(
            supplier.supplier_id,
            0,
        )

        supplier_spend.append(
            {
                "supplier_id": supplier.supplier_id,
                "supplier_name": supplier.supplier_name,
                "reliability_score": float(
                    supplier.reliability_score or 0
                ),
                "purchase_order_value": value,
            }
        )

    supplier_spend.sort(
        key=lambda item: item["purchase_order_value"],
        reverse=True,
    )

    process_flow = {
        "purchase_requisitions": total_requisition_count,
        "purchase_orders": total_po_count,
        "goods_receipts": total_receipt_count,
        "invoices": total_invoice_count,
        "payments": total_payment_count,
    }

    return {
        "overview": {
            "suppliers": total_supplier_count,
            "products": total_product_count,
            "purchase_requisitions": total_requisition_count,
            "purchase_orders": total_po_count,
            "purchase_order_items": len(
                purchase_order_items
            ),
            "goods_receipts": total_receipt_count,
            "invoices": total_invoice_count,
            "payments": total_payment_count,
            "total_purchase_order_value": total_po_value,
            "total_payment_value": total_payment_value,
            "average_purchase_order_value": average_po_value,
        },
        "supplier_intelligence": {
            "average_reliability": average_supplier_reliability,
            "high_risk_suppliers": len(
                high_risk_suppliers
            ),
            "medium_risk_suppliers": len(
                medium_risk_suppliers
            ),
            "reliable_suppliers": len(
                reliable_suppliers
            ),
            "top_suppliers_by_spend": supplier_spend[:5],
        },
        "procurement_intelligence": {
            "complexity_distribution": complexity_distribution,
            "risk_distribution": risk_distribution,
            "approval_route_distribution": (
                approval_route_distribution
            ),
            "high_value_orders": high_value_orders,
        },
        "process_flow": process_flow,
    }