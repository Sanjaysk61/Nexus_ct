from pathlib import Path
from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd
from faker import Faker


fake = Faker()
random.seed(42)
np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EVENT_LOG_DIR = DATA_DIR / "event_logs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
EVENT_LOG_DIR.mkdir(parents=True, exist_ok=True)


NUM_SUPPLIERS = 50
NUM_PRODUCTS = 100
NUM_EMPLOYEES = 100
NUM_PURCHASE_ORDERS = 10000

START_DATE = datetime(2026, 1, 1)


DEPARTMENTS = [
    "IT",
    "Finance",
    "Procurement",
    "Operations",
    "HR",
    "Sales",
    "Marketing",
    "Engineering",
]

WAREHOUSES = [
    "WH-BLR-01",
    "WH-MYS-01",
    "WH-HYD-01",
    "WH-CHN-01",
]

PRODUCT_CATEGORIES = [
    "IT Equipment",
    "Office Supplies",
    "Raw Materials",
    "Packaging",
    "Safety Equipment",
    "Maintenance",
    "Furniture",
]


def generate_suppliers():
    suppliers = []

    for i in range(1, NUM_SUPPLIERS + 1):
        supplier_id = f"SUP-{i:05d}"

        suppliers.append(
            {
                "supplier_id": supplier_id,
                "supplier_name": fake.company(),
                "supplier_country": random.choice(
                    ["India", "Germany", "USA", "Singapore", "UK"]
                ),
                "supplier_category": random.choice(
                    ["Strategic", "Preferred", "Standard", "New"]
                ),
                "reliability_score": round(
                    random.uniform(0.60, 0.99), 2
                ),
                "average_delivery_days": random.randint(2, 15),
            }
        )

    return pd.DataFrame(suppliers)


def generate_products():
    products = []

    for i in range(1, NUM_PRODUCTS + 1):
        products.append(
            {
                "product_id": f"PROD-{i:05d}",
                "product_name": fake.catch_phrase(),
                "category": random.choice(PRODUCT_CATEGORIES),
                "unit_price": round(random.uniform(25, 15000), 2),
                "unit_of_measure": random.choice(
                    ["EA", "BOX", "KG", "SET"]
                ),
            }
        )

    return pd.DataFrame(products)


def generate_employees():
    employees = []

    for i in range(1, NUM_EMPLOYEES + 1):
        employees.append(
            {
                "employee_id": f"EMP-{i:05d}",
                "employee_name": fake.name(),
                "department": random.choice(DEPARTMENTS),
                "role": random.choice(
                    [
                        "Requester",
                        "Manager",
                        "Procurement Specialist",
                        "Finance Analyst",
                        "Warehouse Operator",
                    ]
                ),
            }
        )

    return pd.DataFrame(employees)


def generate_purchase_orders(suppliers, products, employees):
    purchase_requisitions = []
    purchase_orders = []
    purchase_order_items = []

    for i in range(1, NUM_PURCHASE_ORDERS + 1):
        pr_id = f"PR-{i:05d}"
        po_id = f"PO-{i:05d}"

        requester = employees.sample(1).iloc[0]
        supplier = suppliers.sample(1).iloc[0]

        request_date = START_DATE + timedelta(
            days=random.randint(0, 150)
        )

        department = requester["department"]

        approval_delay = random.choice(
            [
                random.randint(1, 3),
                random.randint(1, 5),
                random.randint(2, 15),
            ]
        )

        approval_date = request_date + timedelta(
            days=approval_delay
        )

        po_date = approval_date + timedelta(
            days=random.randint(0, 2)
        )

        product = products.sample(1).iloc[0]

        quantity = random.randint(1, 50)

        amount = round(
            quantity * product["unit_price"],
            2,
        )

        status = random.choices(
            [
                "Completed",
                "Delayed",
                "Cancelled",
            ],
            weights=[0.75, 0.20, 0.05],
        )[0]

        purchase_requisitions.append(
            {
                "pr_id": pr_id,
                "requester_id": requester["employee_id"],
                "department_id": department,
                "supplier_id": supplier["supplier_id"],
                "request_date": request_date,
                "approval_date": approval_date,
                "status": "Approved"
                if status != "Cancelled"
                else "Rejected",
            }
        )

        purchase_orders.append(
            {
                "po_id": po_id,
                "pr_id": pr_id,
                "supplier_id": supplier["supplier_id"],
                "created_by": requester["employee_id"],
                "warehouse_id": random.choice(WAREHOUSES),
                "po_date": po_date,
                "amount": amount,
                "status": status,
            }
        )

        purchase_order_items.append(
            {
                "po_item_id": f"POITEM-{i:05d}",
                "po_id": po_id,
                "product_id": product["product_id"],
                "quantity": quantity,
                "unit_price": product["unit_price"],
                "line_amount": amount,
            }
        )

    return (
        pd.DataFrame(purchase_requisitions),
        pd.DataFrame(purchase_orders),
        pd.DataFrame(purchase_order_items),
    )


def generate_downstream_documents(purchase_orders, suppliers):
    goods_receipts = []
    invoices = []
    payments = []

    for _, po in purchase_orders.iterrows():
        po_id = po["po_id"]

        po_date = pd.Timestamp(po["po_date"])

        supplier = suppliers[
            suppliers["supplier_id"] == po["supplier_id"]
        ].iloc[0]

        supplier_delay = int(
            np.random.normal(
                supplier["average_delivery_days"],
                3,
            )
        )

        supplier_delay = max(1, supplier_delay)

        if po["status"] == "Delayed":
            supplier_delay += random.randint(5, 15)

        receipt_date = po_date + timedelta(
            days=supplier_delay
        )

        goods_receipts.append(
            {
                "gr_id": f"GR-{po_id.replace('PO-', '')}",
                "po_id": po_id,
                "receipt_date": receipt_date,
                "quantity_received": random.randint(1, 50),
                "warehouse_id": po["warehouse_id"],
            }
        )

        invoice_delay = random.randint(1, 5)

        invoice_date = receipt_date + timedelta(
            days=invoice_delay
        )

        mismatch = random.random() < 0.08

        invoice_amount = po["amount"]

        if mismatch:
            invoice_amount = round(
                invoice_amount
                * random.uniform(0.85, 1.15),
                2,
            )

        invoice_id = f"INV-{po_id.replace('PO-', '')}"

        invoices.append(
            {
                "invoice_id": invoice_id,
                "po_id": po_id,
                "invoice_date": invoice_date,
                "invoice_amount": invoice_amount,
                "invoice_status": (
                    "Mismatch"
                    if mismatch
                    else "Verified"
                ),
            }
        )

        verification_delay = (
            random.randint(1, 3)
            if not mismatch
            else random.randint(3, 12)
        )

        payment_delay = random.randint(1, 5)

        payment_date = (
            invoice_date
            + timedelta(days=verification_delay)
            + timedelta(days=payment_delay)
        )

        payments.append(
            {
                "payment_id": f"PAY-{po_id.replace('PO-', '')}",
                "invoice_id": invoice_id,
                "payment_date": payment_date,
                "payment_amount": invoice_amount,
                "payment_status": "Completed",
            }
        )

    return (
        pd.DataFrame(goods_receipts),
        pd.DataFrame(invoices),
        pd.DataFrame(payments),
    )


def generate_process_events(
    purchase_requisitions,
    purchase_orders,
    goods_receipts,
    invoices,
    payments,
    employees,
):
    events = []

    event_counter = 1

    employee_ids = employees["employee_id"].tolist()

    for _, po in purchase_orders.iterrows():
        po_id = po["po_id"]
        pr_id = po["pr_id"]
        supplier_id = po["supplier_id"]

        pr = purchase_requisitions[
            purchase_requisitions["pr_id"] == pr_id
        ].iloc[0]

        gr = goods_receipts[
            goods_receipts["po_id"] == po_id
        ].iloc[0]

        invoice = invoices[
            invoices["po_id"] == po_id
        ].iloc[0]

        payment = payments[
            payments["invoice_id"] == invoice["invoice_id"]
        ].iloc[0]

        current_time = pd.Timestamp(
            pr["request_date"]
        )

        event_sequence = [
            (
                "Purchase Requisition Created",
                current_time,
            ),
            (
                "Purchase Requisition Approved",
                pd.Timestamp(pr["approval_date"]),
            ),
            (
                "Purchase Order Created",
                pd.Timestamp(po["po_date"]),
            ),
        ]

        supplier_confirmation_delay = random.randint(1, 5)

        if po["status"] == "Delayed":
            supplier_confirmation_delay += random.randint(
                5,
                12,
            )

        supplier_confirmation_time = (
            pd.Timestamp(po["po_date"])
            + timedelta(days=supplier_confirmation_delay)
        )

        event_sequence.append(
            (
                "Supplier Confirmation",
                supplier_confirmation_time,
            )
        )

        event_sequence.append(
            (
                "Goods Receipt",
                pd.Timestamp(gr["receipt_date"]),
            )
        )

        event_sequence.append(
            (
                "Invoice Received",
                pd.Timestamp(invoice["invoice_date"]),
            )
        )

        if invoice["invoice_status"] == "Mismatch":
            mismatch_time = (
                pd.Timestamp(invoice["invoice_date"])
                + timedelta(hours=4)
            )

            event_sequence.append(
                (
                    "Invoice Mismatch",
                    mismatch_time,
                )
            )

            manual_time = (
                mismatch_time
                + timedelta(days=random.randint(1, 4))
            )

            event_sequence.append(
                (
                    "Manual Intervention",
                    manual_time,
                )
            )

        event_sequence.append(
            (
                "Invoice Verification",
                pd.Timestamp(invoice["invoice_date"])
                + timedelta(
                    days=(
                        random.randint(1, 3)
                        if invoice["invoice_status"] == "Verified"
                        else random.randint(3, 12)
                    )
                ),
            )
        )

        event_sequence.append(
            (
                "Payment",
                pd.Timestamp(payment["payment_date"]),
            )
        )

        for activity, timestamp in event_sequence:
            events.append(
                {
                    "case_id": po_id.replace(
                        "PO-",
                        "CASE-",
                    ),
                    "event_id": f"EVT-{event_counter:07d}",
                    "activity": activity,
                    "timestamp": timestamp,
                    "resource_id": random.choice(
                        employee_ids
                    ),
                    "supplier_id": supplier_id,
                    "purchase_order_id": po_id,
                    "department_id": pr["department_id"],
                    "amount": po["amount"],
                }
            )

            event_counter += 1

    events_df = pd.DataFrame(events)

    events_df = events_df.sort_values(
        ["case_id", "timestamp"]
    ).reset_index(drop=True)

    return events_df


def save_dataframe(df, filename, directory):
    path = directory / filename
    df.to_csv(path, index=False)
    print(f"Created: {path}")


def main():
    print("=" * 60)
    print("NEXUS - DAY 1 SYNTHETIC DATA GENERATOR")
    print("=" * 60)

    print("\nGenerating suppliers...")
    suppliers = generate_suppliers()

    print("Generating products...")
    products = generate_products()

    print("Generating employees...")
    employees = generate_employees()

    print("Generating purchase requisitions and orders...")
    (
        purchase_requisitions,
        purchase_orders,
        purchase_order_items,
    ) = generate_purchase_orders(
        suppliers,
        products,
        employees,
    )

    print("Generating goods receipts, invoices and payments...")
    (
        goods_receipts,
        invoices,
        payments,
    ) = generate_downstream_documents(
        purchase_orders,
        suppliers,
    )

    print("Generating process event log...")
    process_events = generate_process_events(
        purchase_requisitions,
        purchase_orders,
        goods_receipts,
        invoices,
        payments,
        employees,
    )

    save_dataframe(
        suppliers,
        "suppliers.csv",
        RAW_DIR,
    )

    save_dataframe(
        products,
        "products.csv",
        RAW_DIR,
    )

    save_dataframe(
        employees,
        "employees.csv",
        RAW_DIR,
    )

    save_dataframe(
        purchase_requisitions,
        "purchase_requisitions.csv",
        RAW_DIR,
    )

    save_dataframe(
        purchase_orders,
        "purchase_orders.csv",
        RAW_DIR,
    )

    save_dataframe(
        purchase_order_items,
        "purchase_order_items.csv",
        RAW_DIR,
    )

    save_dataframe(
        goods_receipts,
        "goods_receipts.csv",
        RAW_DIR,
    )

    save_dataframe(
        invoices,
        "invoices.csv",
        RAW_DIR,
    )

    save_dataframe(
        payments,
        "payments.csv",
        RAW_DIR,
    )

    save_dataframe(
        process_events,
        "process_events.csv",
        EVENT_LOG_DIR,
    )

    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE")
    print("=" * 60)

    print(f"\nSuppliers: {len(suppliers):,}")
    print(f"Products: {len(products):,}")
    print(f"Employees: {len(employees):,}")
    print(f"Purchase Orders: {len(purchase_orders):,}")
    print(f"Process Events: {len(process_events):,}")

    print("\nEvent distribution:")
    print(
        process_events["activity"]
        .value_counts()
        .to_string()
    )

    print("\nData generation finished successfully.")


if __name__ == "__main__":
    main()