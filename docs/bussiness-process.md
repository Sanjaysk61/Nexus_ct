# NEXUS Procure-to-Pay Business Process

## Objective

NEXUS analyzes an enterprise Procure-to-Pay process using process mining, machine learning and agentic AI.

## Process

The standard process is:

Purchase Requisition
↓
Approval
↓
Purchase Order
↓
Supplier Confirmation
↓
Goods Receipt
↓
Invoice
↓
Invoice Verification
↓
Payment

## Stage 1 — Purchase Requisition

An employee or department requests goods or services.

Example:

IT requests 20 laptops.

## Stage 2 — Approval

The purchase requisition is reviewed and approved.

Potential problems:

* approval delay
* rejection
* repeated approval
* manual intervention

## Stage 3 — Purchase Order

After approval, procurement creates a purchase order for the supplier.

Potential problems:

* duplicate PO
* incorrect amount
* cancellation

## Stage 4 — Supplier Confirmation

The supplier confirms the purchase order.

Potential problems:

* supplier delay
* supplier rejection
* incomplete confirmation

## Stage 5 — Goods Receipt

The organization receives the ordered goods.

Potential problems:

* late delivery
* partial receipt
* missing receipt

## Stage 6 — Invoice

The supplier submits an invoice.

Potential problems:

* invoice mismatch
* duplicate invoice
* incorrect amount

## Stage 7 — Invoice Verification

The invoice is checked against the purchase order and goods receipt.

Potential problems:

* quantity mismatch
* price mismatch
* manual intervention

## Stage 8 — Payment

The approved invoice is paid.

Potential problems:

* payment delay
* blocked invoice
* exception handling

## Process Intelligence Questions

NEXUS should eventually answer:

1. What is happening?
2. Where are delays occurring?
3. Which process variant is common?
4. Which suppliers create delays?
5. What is the average cycle time?
6. Why is a case delayed?
7. Which cases are anomalous?
8. What is likely to happen next?
9. What action should be considered?
10. Does the proposed action require human approval?
