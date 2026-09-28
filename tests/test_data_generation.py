from data.generate_data import generate_dataset


def test_generate_dataset():

    dataset = generate_dataset()

    assert len(dataset["suppliers"]) == 10
    assert len(dataset["products"]) == 20
    assert len(dataset["employees"]) == 15
    assert len(dataset["purchase_requisitions"]) == 25
    assert len(dataset["purchase_orders"]) == 25
    assert len(dataset["purchase_order_items"]) == 25
    assert len(dataset["goods_receipts"]) == 25
    assert len(dataset["invoices"]) == 25
    assert len(dataset["payments"]) == 25


def test_purchase_order_references_requisition():

    dataset = generate_dataset()

    requisition_ids = {
        requisition["requisition_id"]
        for requisition in dataset["purchase_requisitions"]
    }

    for purchase_order in dataset["purchase_orders"]:
        assert (
            purchase_order["requisition_id"]
            in requisition_ids
        )


def test_invoice_references_purchase_order():

    dataset = generate_dataset()

    purchase_order_ids = {
        purchase_order["purchase_order_id"]
        for purchase_order in dataset["purchase_orders"]
    }

    for invoice in dataset["invoices"]:
        assert (
            invoice["purchase_order_id"]
            in purchase_order_ids
        )


def test_payment_references_invoice():

    dataset = generate_dataset()

    invoice_ids = {
        invoice["invoice_id"]
        for invoice in dataset["invoices"]
    }

    for payment in dataset["payments"]:
        assert payment["invoice_id"] in invoice_ids