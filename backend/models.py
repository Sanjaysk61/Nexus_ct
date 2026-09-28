from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(String, primary_key=True)
    supplier_name = Column(String, nullable=False)
    contact_name = Column(String)
    email = Column(String)
    country = Column(String)
    city = Column(String)
    reliability_score = Column(Float)


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True)
    product_name = Column(String, nullable=False)
    category = Column(String)
    unit_price = Column(Float)
    supplier_id = Column(
        String,
        ForeignKey("suppliers.supplier_id"),
        nullable=False,
    )


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True)
    employee_name = Column(String, nullable=False)
    department = Column(String)
    role = Column(String)


class PurchaseRequisition(Base):
    __tablename__ = "purchase_requisitions"

    requisition_id = Column(String, primary_key=True)
    employee_id = Column(
        String,
        ForeignKey("employees.employee_id"),
        nullable=False,
    )
    department = Column(String)
    product_id = Column(
        String,
        ForeignKey("products.product_id"),
        nullable=False,
    )
    quantity = Column(Integer)
    estimated_amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    purchase_order_id = Column(String, primary_key=True)
    requisition_id = Column(
        String,
        ForeignKey("purchase_requisitions.requisition_id"),
        nullable=False,
    )
    supplier_id = Column(
        String,
        ForeignKey("suppliers.supplier_id"),
        nullable=False,
    )
    order_date = Column(DateTime)
    total_amount = Column(Float)
    currency = Column(String)
    status = Column(String)


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    po_item_id = Column(String, primary_key=True)
    purchase_order_id = Column(
        String,
        ForeignKey("purchase_orders.purchase_order_id"),
        nullable=False,
    )
    product_id = Column(
        String,
        ForeignKey("products.product_id"),
        nullable=False,
    )
    quantity = Column(Integer)
    unit_price = Column(Float)
    line_amount = Column(Float)


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    goods_receipt_id = Column(String, primary_key=True)
    purchase_order_id = Column(
        String,
        ForeignKey("purchase_orders.purchase_order_id"),
        nullable=False,
    )
    warehouse = Column(String)
    receipt_date = Column(DateTime)
    received_quantity = Column(Integer)


class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id = Column(String, primary_key=True)
    purchase_order_id = Column(
        String,
        ForeignKey("purchase_orders.purchase_order_id"),
        nullable=False,
    )
    invoice_number = Column(String, unique=True)
    invoice_date = Column(DateTime)
    invoice_amount = Column(Float)
    status = Column(String)


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(String, primary_key=True)
    invoice_id = Column(
        String,
        ForeignKey("invoices.invoice_id"),
        nullable=False,
    )
    payment_date = Column(DateTime)
    payment_amount = Column(Float)
    status = Column(String)


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(String, primary_key=True)
    product_id = Column(
        String,
        ForeignKey("products.product_id"),
        nullable=False,
    )
    warehouse = Column(String)
    quantity = Column(Integer)


class ProcessEvent(Base):
    __tablename__ = "process_events"

    event_id = Column(String, primary_key=True)
    case_id = Column(String, nullable=False)
    activity = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    resource_id = Column(String, nullable=False)
    supplier_id = Column(
        String,
        ForeignKey("suppliers.supplier_id"),
    )
    purchase_order_id = Column(
        String,
        ForeignKey("purchase_orders.purchase_order_id"),
    )
    department_id = Column(String)
    amount = Column(Float)


class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"

    decision_id = Column(Integer, primary_key=True, autoincrement=True)

    purchase_order_id = Column(
        String,
        ForeignKey("purchase_orders.purchase_order_id"),
        nullable=False,
    )

    decision = Column(
        String,
        nullable=False,
    )

    reviewer_id = Column(
        String,
        nullable=False,
    )

    comments = Column(String)

    decided_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )