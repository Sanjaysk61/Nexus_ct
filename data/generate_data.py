from datetime import datetime, timedelta
from decimal import Decimal
import random

from faker import Faker

fake = Faker("en_IN")

random.seed(42)
Faker.seed(42)


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

NUM_SUPPLIERS = 10
NUM_PRODUCTS = 20
NUM_EMPLOYEES = 15
NUM_PURCHASE_REQUISITIONS = 25


DEPARTMENTS = [
    "Procurement",
    "IT",
    "Finance",
    "Operations",
    "Warehouse",
    "Human Resources",
]


WAREHOUSES = [
    "WH-Bangalore",
    "WH-Chennai",
    "WH-Hyderabad",
]


PRODUCT_CATEGORIES = [
    "IT Equipment",
    "Office Supplies",
    "Industrial Equipment",
    "Packaging",
    "Safety Equipment",
]


# ---------------------------------------------------------
# ID GENERATORS
# ---------------------------------------------------------

def generate_id(prefix, number):
    return f"{prefix}-{number:05d}"


# ---------------------------------------------------------
# SUPPLIERS
# ---------------------------------------------------------

def generate_suppliers():
    suppliers = []

    for i in range(1, NUM_SUPPLIERS + 1):
        suppliers.append(
            {
                "supplier_id": generate_id("SUP", i),
                "supplier_name": fake.company(),
                "contact_name": fake.name(),
                "email": fake.company_email(),
                "country": "India",
                "city": fake.city(),
                "reliability_score": round(random.uniform(0.65, 0.98), 2),
            }
        )

    return suppliers


# ---------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------

def generate_products():
    products = []

    for i in range(1, NUM_PRODUCTS + 1):
        category = random.choice(PRODUCT_CATEGORIES)

        products.append(
            {
                "product_id": generate_id("PROD", i),
                "product_name": fake.catch_phrase(),
                "category": category,
                "unit_price": round(
                    random.uniform(500, 100000),
                    2
                ),
                "supplier_id": generate_id(
                    "SUP",
                    random.randint(1, NUM_SUPPLIERS)
                ),
            }
        )

    return products


# ---------------------------------------------------------
# EMPLOYEES
# ---------------------------------------------------------

def generate_employees():
    employees = []

    for i in range(1, NUM_EMPLOYEES + 1):
        employees.append(
            {
                "employee_id": generate_id("EMP", i),
                "employee_name": fake.name(),
                "department": random.choice(DEPARTMENTS),
                "role": random.choice(
                    [
                        "Requester",
                        "Manager",
                        "Procurement Officer",
                        "Finance Analyst",
                        "Operations Analyst",
                    ]
                ),
            }
        )

    return employees


# ---------------------------------------------------------
# PURCHASE REQUISITIONS
# ---------------------------------------------------------

def generate_purchase_requisitions(products, employees):
    requisitions = []

    start_date = datetime.now() - timedelta(days=90)

    for i in range(1, NUM_PURCHASE_REQUISITIONS + 1):

        employee = random.choice(employees)
        product = random.choice(products)

        quantity = random.randint(1, 20)

        created_at = start_date + timedelta(
            days=random.randint(0, 80),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        requisitions.append(
            {
                "requisition_id": generate_id("PR", i),
                "employee_id": employee["employee_id"],
                "department": employee["department"],
                "product_id": product["product_id"],
                "quantity": quantity,
                "estimated_amount": round(
                    product["unit_price"] * quantity,
                    2
                ),
                "status": "APPROVED",
                "created_at": created_at,
            }
        )

    return requisitions


# ---------------------------------------------------------
# PURCHASE ORDERS
# ---------------------------------------------------------

def generate_purchase_orders(requisitions, products):
    purchase_orders = []

    for i, requisition in enumerate(requisitions, start=1):

        product = next(
            p
            for p in products
            if p["product_id"] == requisition["product_id"]
        )

        po_date = requisition["created_at"] + timedelta(
            days=random.randint(1, 5)
        )

        quantity = requisition["quantity"]

        total_amount = round(
            product["unit_price"] * quantity,
            2
        )

        purchase_orders.append(
            {
                "purchase_order_id": generate_id("PO", i),
                "requisition_id": requisition["requisition_id"],
                "supplier_id": product["supplier_id"],
                "order_date": po_date,
                "total_amount": total_amount,
                "currency": "INR",
                "status": "CONFIRMED",
            }
        )

    return purchase_orders


# ---------------------------------------------------------
# PURCHASE ORDER ITEMS
# ---------------------------------------------------------

def generate_purchase_order_items(
    purchase_orders,
    requisitions,
    products
):
    items = []

    for po in purchase_orders:

        requisition = next(
            r
            for r in requisitions
            if r["requisition_id"] == po["requisition_id"]
        )

        product = next(
            p
            for p in products
            if p["product_id"] == requisition["product_id"]
        )

        items.append(
            {
                "po_item_id": generate_id(
                    "ITEM",
                    len(items) + 1
                ),
                "purchase_order_id": po[
                    "purchase_order_id"
                ],
                "product_id": product["product_id"],
                "quantity": requisition["quantity"],
                "unit_price": product["unit_price"],
                "line_amount": round(
                    requisition["quantity"]
                    * product["unit_price"],
                    2,
                ),
            }
        )

    return items


# ---------------------------------------------------------
# GOODS RECEIPTS
# ---------------------------------------------------------

def generate_goods_receipts(purchase_orders):
    receipts = []

    for i, po in enumerate(purchase_orders, start=1):

        receipt_date = po["order_date"] + timedelta(
            days=random.randint(2, 15)
        )

        receipts.append(
            {
                "goods_receipt_id": generate_id("GR", i),
                "purchase_order_id": po[
                    "purchase_order_id"
                ],
                "warehouse": random.choice(WAREHOUSES),
                "receipt_date": receipt_date,
                "received_quantity": random.randint(1, 20),
            }
        )

    return receipts


# ---------------------------------------------------------
# INVOICES
# ---------------------------------------------------------

def generate_invoices(purchase_orders):
    invoices = []

    for i, po in enumerate(purchase_orders, start=1):

        invoice_date = po["order_date"] + timedelta(
            days=random.randint(5, 18)
        )

        invoices.append(
            {
                "invoice_id": generate_id("INV", i),
                "purchase_order_id": po[
                    "purchase_order_id"
                ],
                "invoice_number": f"INV-{random.randint(100000, 999999)}",
                "invoice_date": invoice_date,
                "invoice_amount": po["total_amount"],
                "status": "VERIFIED",
            }
        )

    return invoices


# ---------------------------------------------------------
# PAYMENTS
# ---------------------------------------------------------

def generate_payments(invoices):
    payments = []

    for i, invoice in enumerate(invoices, start=1):

        payment_date = invoice["invoice_date"] + timedelta(
            days=random.randint(2, 10)
        )

        payments.append(
            {
                "payment_id": generate_id("PAY", i),
                "invoice_id": invoice["invoice_id"],
                "payment_date": payment_date,
                "payment_amount": invoice["invoice_amount"],
                "status": "PAID",
            }
        )

    return payments


# ---------------------------------------------------------
# COMPLETE DATASET
# ---------------------------------------------------------

def generate_dataset():

    suppliers = generate_suppliers()

    products = generate_products()

    employees = generate_employees()

    requisitions = generate_purchase_requisitions(
        products,
        employees,
    )

    purchase_orders = generate_purchase_orders(
        requisitions,
        products,
    )

    purchase_order_items = generate_purchase_order_items(
        purchase_orders,
        requisitions,
        products,
    )

    goods_receipts = generate_goods_receipts(
        purchase_orders
    )

    invoices = generate_invoices(
        purchase_orders
    )

    payments = generate_payments(
        invoices
    )

    return {
        "suppliers": suppliers,
        "products": products,
        "employees": employees,
        "purchase_requisitions": requisitions,
        "purchase_orders": purchase_orders,
        "purchase_order_items": purchase_order_items,
        "goods_receipts": goods_receipts,
        "invoices": invoices,
        "payments": payments,
    }


# ---------------------------------------------------------
# DISPLAY SUMMARY
# ---------------------------------------------------------

def main():

    dataset = generate_dataset()

    print("\n========================================")
    print("       NEXUS SYNTHETIC DATA")
    print("========================================")

    for table_name, records in dataset.items():
        print(
            f"{table_name:<25} : {len(records)} records"
        )

    print("========================================")

    print("\nSample Purchase Order:")

    print(dataset["purchase_orders"][0])

    print("\nSample Supplier:")

    print(dataset["suppliers"][0])

    print("\nSample Invoice:")

    print(dataset["invoices"][0])


if __name__ == "__main__":
    main()