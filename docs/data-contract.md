# NEXUS Data Contract

## 1. Purpose

This document defines the shared data contract for the NEXUS Process Intelligence system.

NEXUS monitors an enterprise Procure-to-Pay process.

## 2. Procure-to-Pay Process

The primary process is:

Purchase Requisition
→ Approval
→ Purchase Order
→ Supplier Confirmation
→ Goods Receipt
→ Invoice
→ Invoice Verification
→ Payment

## 3. Core Entities

NEXUS initially uses the following entities:

* Suppliers
* Products
* Employees
* Purchase Requisitions
* Purchase Orders
* Purchase Order Items
* Goods Receipts
* Invoices
* Payments
* Process Events

## 4. Shared Identifier Format

Suppliers:

SUP-00001

Products:

PROD-00001

Employees:

EMP-00001

Purchase Requisitions:

PR-00001

Purchase Orders:

PO-00001

Invoices:

INV-00001

Payments:

PAY-00001

Process Cases:

CASE-00001

Process Events:

EVT-00001

## 5. Process Event Schema

Every process event must contain:

* case_id
* event_id
* activity
* timestamp
* resource_id

Additional fields:

* supplier_id
* purchase_order_id
* department_id
* amount

## 6. Event Activities

The initial P2P event vocabulary is:

* Purchase Requisition Created
* Purchase Requisition Approved
* Purchase Order Created
* Supplier Confirmation
* Goods Receipt
* Invoice Received
* Invoice Verification
* Payment

Exception activities may include:

* Purchase Requisition Rejected
* Purchase Order Cancelled
* Invoice Mismatch
* Manual Intervention

## 7. Process Case

A case represents one P2P transaction journey.

For the initial implementation:

case_id = one purchase order process journey.

## 8. Data Generation

The initial synthetic dataset targets:

* 10,000 purchase orders
* 50 suppliers
* 100 products
* multiple departments
* multiple employees
* multiple warehouses
* 50,000+ process events

The generated data must contain realistic relationships.

## 9. Process Problems

Synthetic data should contain controlled process problems:

* approval delays
* supplier delays
* invoice mismatches
* purchase-order cancellations
* repeated approvals
* goods-receipt delays
* payment delays
* process deviations

## 10. Process Mining Compatibility

The event log must be compatible with PM4Py.

The mandatory PM4Py concepts are:

Case ID:
case_id

Activity:
activity

Timestamp:
timestamp

Resource:
resource_id

## 11. Data Ownership

Person 1 owns the initial data foundation and process-intelligence data contract.

Other modules must consume this contract rather than independently creating incompatible schemas.

## 12. Change Policy

Changes to shared identifiers, event names or core columns must be documented before implementation.

No module should silently rename shared fields.
