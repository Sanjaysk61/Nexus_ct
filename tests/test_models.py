from sqlalchemy import inspect

from backend.database import engine
from backend.models import Base


def test_create_nexus_tables():
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)

    expected_tables = {
        "suppliers",
        "employees",
        "products",
        "purchase_requisitions",
        "purchase_orders",
        "purchase_order_items",
        "goods_receipts",
        "invoices",
        "payments",
        "process_events",
    }

    actual_tables = set(inspector.get_table_names())

    assert expected_tables.issubset(actual_tables)