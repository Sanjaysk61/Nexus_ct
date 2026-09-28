from sqlalchemy import func

from backend.database import SessionLocal
from backend.models import (
    Supplier,
    Product,
    Employee,
    PurchaseRequisition,
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceipt,
    Invoice,
    Payment,
)


def test_data_counts():
    session = SessionLocal()

    try:
        assert session.query(func.count(Supplier.supplier_id)).scalar() == 10
        assert session.query(func.count(Product.product_id)).scalar() == 20
        assert session.query(func.count(Employee.employee_id)).scalar() == 15
        assert session.query(func.count(PurchaseRequisition.requisition_id)).scalar() == 25
        assert session.query(func.count(PurchaseOrder.purchase_order_id)).scalar() == 25
        assert session.query(func.count(PurchaseOrderItem.po_item_id)).scalar() == 25
        assert session.query(func.count(GoodsReceipt.goods_receipt_id)).scalar() == 25
        assert session.query(func.count(Invoice.invoice_id)).scalar() == 25
        assert session.query(func.count(Payment.payment_id)).scalar() == 25

    finally:
        session.close()


def test_purchase_orders_reference_requisitions():
    session = SessionLocal()

    try:
        purchase_orders = session.query(PurchaseOrder).all()

        for po in purchase_orders:
            requisition = session.get(
                PurchaseRequisition,
                po.requisition_id,
            )

            assert requisition is not None

    finally:
        session.close()


def test_purchase_orders_reference_suppliers():
    session = SessionLocal()

    try:
        purchase_orders = session.query(PurchaseOrder).all()

        for po in purchase_orders:
            supplier = session.get(
                Supplier,
                po.supplier_id,
            )

            assert supplier is not None

    finally:
        session.close()


def test_purchase_order_items_reference_purchase_orders():
    session = SessionLocal()

    try:
        items = session.query(PurchaseOrderItem).all()

        for item in items:
            purchase_order = session.get(
                PurchaseOrder,
                item.purchase_order_id,
            )

            assert purchase_order is not None

    finally:
        session.close()


def test_goods_receipts_reference_purchase_orders():
    session = SessionLocal()

    try:
        receipts = session.query(GoodsReceipt).all()

        for receipt in receipts:
            purchase_order = session.get(
                PurchaseOrder,
                receipt.purchase_order_id,
            )

            assert purchase_order is not None

    finally:
        session.close()


def test_invoices_reference_purchase_orders():
    session = SessionLocal()

    try:
        invoices = session.query(Invoice).all()

        for invoice in invoices:
            purchase_order = session.get(
                PurchaseOrder,
                invoice.purchase_order_id,
            )

            assert purchase_order is not None

    finally:
        session.close()


def test_payments_reference_invoices():
    session = SessionLocal()

    try:
        payments = session.query(Payment).all()

        for payment in payments:
            invoice = session.get(
                Invoice,
                payment.invoice_id,
            )

            assert invoice is not None

    finally:
        session.close()