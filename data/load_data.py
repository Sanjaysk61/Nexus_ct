from sqlalchemy.orm import Session

from backend.database import engine
from backend.models import (
    Base,
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

from data.generate_data import generate_dataset


def load_data():
    Base.metadata.create_all(bind=engine)

    dataset = generate_dataset()

    with Session(engine) as session:
        try:
            suppliers = [
                Supplier(**record)
                for record in dataset["suppliers"]
            ]

            products = [
                Product(**record)
                for record in dataset["products"]
            ]

            employees = [
                Employee(**record)
                for record in dataset["employees"]
            ]

            requisitions = [
                PurchaseRequisition(**record)
                for record in dataset["purchase_requisitions"]
            ]

            purchase_orders = [
                PurchaseOrder(**record)
                for record in dataset["purchase_orders"]
            ]

            purchase_order_items = [
                PurchaseOrderItem(**record)
                for record in dataset["purchase_order_items"]
            ]

            goods_receipts = [
                GoodsReceipt(**record)
                for record in dataset["goods_receipts"]
            ]

            invoices = [
                Invoice(**record)
                for record in dataset["invoices"]
            ]

            payments = [
                Payment(**record)
                for record in dataset["payments"]
            ]

            session.add_all(suppliers)
            session.flush()

            session.add_all(products)
            session.flush()

            session.add_all(employees)
            session.flush()

            session.add_all(requisitions)
            session.flush()

            session.add_all(purchase_orders)
            session.flush()

            session.add_all(purchase_order_items)
            session.flush()

            session.add_all(goods_receipts)
            session.flush()

            session.add_all(invoices)
            session.flush()

            session.add_all(payments)
            session.flush()

            session.commit()

            print("\n========================================")
            print("       NEXUS DATA LOAD SUCCESSFUL")
            print("========================================")

            print(
                f"Suppliers              : {len(suppliers)}"
            )
            print(
                f"Products               : {len(products)}"
            )
            print(
                f"Employees              : {len(employees)}"
            )
            print(
                f"Purchase Requisitions  : {len(requisitions)}"
            )
            print(
                f"Purchase Orders       : {len(purchase_orders)}"
            )
            print(
                f"Purchase Order Items  : {len(purchase_order_items)}"
            )
            print(
                f"Goods Receipts        : {len(goods_receipts)}"
            )
            print(
                f"Invoices              : {len(invoices)}"
            )
            print(
                f"Payments              : {len(payments)}"
            )

            print("========================================")

        except Exception as e:
            session.rollback()
            print("\n========================================")
            print("          DATA LOAD FAILED")
            print("========================================")
            print(f"Error: {e}")
            print("========================================")
            raise


if __name__ == "__main__":
    load_data()