from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List

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
    ProcessEvent,
)

from backend.services.procurement_engine import (
    analyze_purchase_order,
)


try:
    import pandas as pd
    import pm4py

    PM4PY_AVAILABLE = True

except ImportError:
    pd = None
    pm4py = None
    PM4PY_AVAILABLE = False


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _safe_datetime(value: Any):
    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _build_event_log(
    process_events: List[ProcessEvent],
) -> List[Dict[str, Any]]:

    event_log = []

    for event in process_events:

        timestamp = _safe_datetime(
            event.timestamp
        )

        if not timestamp:
            continue

        event_log.append(
            {
                "case_id": event.case_id,
                "activity": event.activity,
                "timestamp": timestamp,
                "resource_id": event.resource_id,
                "supplier_id": event.supplier_id,
                "purchase_order_id": (
                    event.purchase_order_id
                ),
                "department_id": event.department_id,
                "amount": _safe_float(event.amount),
            }
        )

    event_log.sort(
        key=lambda item: (
            item["case_id"],
            item["timestamp"],
        )
    )

    return event_log


def _calculate_activity_frequency(
    event_log: List[Dict[str, Any]],
):

    counter = Counter(
        event["activity"]
        for event in event_log
    )

    return [
        {
            "activity": activity,
            "event_count": count,
        }
        for activity, count
        in counter.most_common()
    ]


def _calculate_directly_follows(
    event_log: List[Dict[str, Any]],
):

    cases = defaultdict(list)

    for event in event_log:
        cases[event["case_id"]].append(event)

    transitions = Counter()

    for case_events in cases.values():

        case_events.sort(
            key=lambda item: item["timestamp"]
        )

        for index in range(
            len(case_events) - 1
        ):

            source = case_events[index][
                "activity"
            ]

            target = case_events[index + 1][
                "activity"
            ]

            transitions[
                (source, target)
            ] += 1

    return [
        {
            "from_activity": source,
            "to_activity": target,
            "frequency": frequency,
        }
        for (
            source,
            target
        ), frequency
        in transitions.most_common()
    ]


def _calculate_start_end_activities(
    event_log: List[Dict[str, Any]],
):

    cases = defaultdict(list)

    for event in event_log:
        cases[event["case_id"]].append(event)

    start_counter = Counter()
    end_counter = Counter()

    for case_events in cases.values():

        case_events.sort(
            key=lambda item: item["timestamp"]
        )

        if not case_events:
            continue

        start_counter[
            case_events[0]["activity"]
        ] += 1

        end_counter[
            case_events[-1]["activity"]
        ] += 1

    return {
        "start_activities": [
            {
                "activity": activity,
                "case_count": count,
            }
            for activity, count
            in start_counter.most_common()
        ],
        "end_activities": [
            {
                "activity": activity,
                "case_count": count,
            }
            for activity, count
            in end_counter.most_common()
        ],
    }


def _calculate_case_durations(
    event_log: List[Dict[str, Any]],
):

    cases = defaultdict(list)

    for event in event_log:
        cases[event["case_id"]].append(event)

    durations = []

    for case_id, case_events in cases.items():

        case_events.sort(
            key=lambda item: item["timestamp"]
        )

        if len(case_events) < 2:
            continue

        start_time = case_events[0]["timestamp"]
        end_time = case_events[-1]["timestamp"]

        duration_hours = (
            end_time - start_time
        ).total_seconds() / 3600

        durations.append(
            {
                "case_id": case_id,
                "duration_hours": round(
                    duration_hours,
                    2,
                ),
            }
        )

    if not durations:

        return {
            "average_cycle_time_hours": 0,
            "minimum_cycle_time_hours": 0,
            "maximum_cycle_time_hours": 0,
            "cases_with_duration": 0,
            "long_running_cases": [],
        }

    duration_values = [
        item["duration_hours"]
        for item in durations
    ]

    average_duration = (
        sum(duration_values)
        / len(duration_values)
    )

    long_running_cases = sorted(
        durations,
        key=lambda item: item[
            "duration_hours"
        ],
        reverse=True,
    )[:10]

    return {
        "average_cycle_time_hours": round(
            average_duration,
            2,
        ),
        "minimum_cycle_time_hours": round(
            min(duration_values),
            2,
        ),
        "maximum_cycle_time_hours": round(
            max(duration_values),
            2,
        ),
        "cases_with_duration": len(
            durations
        ),
        "long_running_cases": (
            long_running_cases
        ),
    }


def _detect_process_bottlenecks(
    event_log: List[Dict[str, Any]],
):

    cases = defaultdict(list)

    for event in event_log:
        cases[event["case_id"]].append(event)

    transition_durations = defaultdict(list)

    for case_events in cases.values():

        case_events.sort(
            key=lambda item: item["timestamp"]
        )

        for index in range(
            len(case_events) - 1
        ):

            current_event = case_events[
                index
            ]

            next_event = case_events[
                index + 1
            ]

            duration_hours = (
                next_event["timestamp"]
                - current_event["timestamp"]
            ).total_seconds() / 3600

            transition = (
                current_event["activity"],
                next_event["activity"],
            )

            transition_durations[
                transition
            ].append(duration_hours)

    bottlenecks = []

    for transition, durations in (
        transition_durations.items()
    ):

        if not durations:
            continue

        average_hours = (
            sum(durations)
            / len(durations)
        )

        if average_hours < 24:
            continue

        bottlenecks.append(
            {
                "from_activity": transition[0],
                "to_activity": transition[1],
                "average_waiting_hours": round(
                    average_hours,
                    2,
                ),
                "observations": len(
                    durations
                ),
                "severity": (
                    "HIGH"
                    if average_hours >= 72
                    else "MEDIUM"
                ),
                "recommended_action": (
                    "Investigate process delay "
                    "between these activities."
                ),
            }
        )

    bottlenecks.sort(
        key=lambda item: item[
            "average_waiting_hours"
        ],
        reverse=True,
    )

    return bottlenecks[:10]


def _calculate_process_variants(
    event_log: List[Dict[str, Any]],
):

    cases = defaultdict(list)

    for event in event_log:
        cases[event["case_id"]].append(event)

    variants = Counter()

    for case_events in cases.values():

        case_events.sort(
            key=lambda item: item["timestamp"]
        )

        activities = tuple(
            event["activity"]
            for event in case_events
        )

        if activities:
            variants[activities] += 1

    result = []

    for variant, count in (
        variants.most_common(10)
    ):

        result.append(
            {
                "variant": list(variant),
                "case_count": count,
            }
        )

    return result


def _run_pm4py_analysis(
    event_log: List[Dict[str, Any]],
):

    if not PM4PY_AVAILABLE:

        return {
            "available": False,
            "message": (
                "PM4Py is not installed. "
                "Install pm4py to enable "
                "process discovery."
            ),
        }

    if not event_log:

        return {
            "available": True,
            "message": (
                "No process events available "
                "for PM4Py analysis."
            ),
        }

    try:

        dataframe = pd.DataFrame(
            event_log
        )

        dataframe = dataframe.rename(
            columns={
                "case_id": "case:concept:name",
                "activity": "concept:name",
                "timestamp": "time:timestamp",
                "resource_id": "org:resource",
            }
        )

        dataframe[
            "time:timestamp"
        ] = pd.to_datetime(
            dataframe["time:timestamp"]
        )

        dataframe = pm4py.format_dataframe(
            dataframe,
            case_id="case:concept:name",
            activity_key="concept:name",
            timestamp_key="time:timestamp",
        )

        activities = sorted(
            dataframe[
                "concept:name"
            ]
            .dropna()
            .unique()
            .tolist()
        )

        case_count = (
            dataframe[
                "case:concept:name"
            ].nunique()
        )

        event_count = len(
            dataframe
        )

        process_tree = None

        try:

            process_tree = (
                pm4py.discover_process_tree_inductive(
                    dataframe
                )
            )

        except Exception:
            process_tree = None

        process_tree_available = (
            process_tree is not None
        )

        return {
            "available": True,
            "engine": "PM4Py",
            "discovery_algorithm": (
                "Inductive Miner"
            ),
            "event_count": event_count,
            "case_count": case_count,
            "activity_count": len(
                activities
            ),
            "activities": activities,
            "process_tree_discovered": (
                process_tree_available
            ),
            "process_model": (
                "Inductive Miner process tree"
                if process_tree_available
                else None
            ),
        }

    except Exception as error:

        return {
            "available": True,
            "engine": "PM4Py",
            "analysis_status": "ERROR",
            "error": str(error),
        }


def _build_celonis_event_log(
    event_log: List[Dict[str, Any]],
):

    celonis_events = []

    for event in event_log:

        celonis_events.append(
            {
                "case_id": event[
                    "case_id"
                ],
                "activity": event[
                    "activity"
                ],
                "timestamp": (
                    event[
                        "timestamp"
                    ].isoformat()
                ),
                "resource_id": event[
                    "resource_id"
                ],
                "supplier_id": event[
                    "supplier_id"
                ],
                "purchase_order_id": event[
                    "purchase_order_id"
                ],
                "department_id": event[
                    "department_id"
                ],
                "amount": event[
                    "amount"
                ],
            }
        )

    return celonis_events


def _build_celonis_integration_metadata(
    event_log: List[Dict[str, Any]],
):

    return {
        "platform": "Celonis",
        "integration_status": (
            "EVENT_LOG_READY"
        ),
        "event_count": len(
            event_log
        ),
        "required_case_column": (
            "case_id"
        ),
        "required_activity_column": (
            "activity"
        ),
        "required_timestamp_column": (
            "timestamp"
        ),
        "recommended_case_key": (
            "purchase_order_id"
        ),
        "source": (
            "NEXUS ProcessEvent database"
        ),
        "message": (
            "Event data is structured in a "
            "Celonis-compatible process-mining "
            "format. Live Celonis data-pool "
            "connection can be configured "
            "separately."
        ),
    }


def generate_process_intelligence(
    db: Session,
):

    suppliers = db.query(
        Supplier
    ).all()

    products = db.query(
        Product
    ).all()

    requisitions = db.query(
        PurchaseRequisition
    ).all()

    purchase_orders = db.query(
        PurchaseOrder
    ).all()

    purchase_order_items = db.query(
        PurchaseOrderItem
    ).all()

    goods_receipts = db.query(
        GoodsReceipt
    ).all()

    invoices = db.query(
        Invoice
    ).all()

    payments = db.query(
        Payment
    ).all()

    process_events = db.query(
        ProcessEvent
    ).all()

    total_supplier_count = len(
        suppliers
    )

    total_product_count = len(
        products
    )

    total_requisition_count = len(
        requisitions
    )

    total_po_count = len(
        purchase_orders
    )

    total_receipt_count = len(
        goods_receipts
    )

    total_invoice_count = len(
        invoices
    )

    total_payment_count = len(
        payments
    )

    total_event_count = len(
        process_events
    )

    total_po_value = sum(
        float(
            po.total_amount or 0
        )
        for po in purchase_orders
    )

    total_payment_value = sum(
        float(
            payment.payment_amount or 0
        )
        for payment in payments
    )

    average_po_value = (
        total_po_value / total_po_count
        if total_po_count
        else 0
    )

    supplier_reliability = [
        float(
            supplier.reliability_score or 0
        )
        for supplier in suppliers
    ]

    average_supplier_reliability = (
        sum(
            supplier_reliability
        )
        / len(
            supplier_reliability
        )
        if supplier_reliability
        else 0
    )

    high_risk_suppliers = [
        supplier
        for supplier in suppliers
        if float(
            supplier.reliability_score or 0
        ) < 0.70
    ]

    medium_risk_suppliers = [
        supplier
        for supplier in suppliers
        if 0.70 <= float(
            supplier.reliability_score or 0
        ) < 0.85
    ]

    reliable_suppliers = [
        supplier
        for supplier in suppliers
        if float(
            supplier.reliability_score or 0
        ) >= 0.85
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

        complexity = assessment[
            "complexity"
        ]

        risk_level = assessment[
            "risk_level"
        ]

        approval_route = assessment[
            "approval_route"
        ]

        if (
            complexity
            in complexity_distribution
        ):
            complexity_distribution[
                complexity
            ] += 1

        if (
            risk_level
            in risk_distribution
        ):
            risk_distribution[
                risk_level
            ] += 1

        if (
            approval_route
            in approval_route_distribution
        ):
            approval_route_distribution[
                approval_route
            ] += 1

        procurement_assessments.append(
            assessment
        )

    high_value_orders = sorted(
        procurement_assessments,
        key=lambda item: item[
            "purchase_order_value"
        ],
        reverse=True,
    )[:5]

    supplier_po_value = {}

    for purchase_order in purchase_orders:

        supplier_id = (
            purchase_order.supplier_id
        )

        supplier_po_value[
            supplier_id
        ] = (
            supplier_po_value.get(
                supplier_id,
                0,
            )
            + float(
                purchase_order.total_amount
                or 0
            )
        )

    supplier_spend = []

    for supplier in suppliers:

        value = supplier_po_value.get(
            supplier.supplier_id,
            0,
        )

        supplier_spend.append(
            {
                "supplier_id": (
                    supplier.supplier_id
                ),
                "supplier_name": (
                    supplier.supplier_name
                ),
                "reliability_score": float(
                    supplier.reliability_score
                    or 0
                ),
                "purchase_order_value": (
                    value
                ),
            }
        )

    supplier_spend.sort(
        key=lambda item: item[
            "purchase_order_value"
        ],
        reverse=True,
    )

    process_flow = {
        "purchase_requisitions": (
            total_requisition_count
        ),
        "purchase_orders": (
            total_po_count
        ),
        "goods_receipts": (
            total_receipt_count
        ),
        "invoices": (
            total_invoice_count
        ),
        "payments": (
            total_payment_count
        ),
    }

    bottlenecks = []

    if (
        total_requisition_count
        > total_po_count
    ):

        bottlenecks.append(
            {
                "stage": (
                    "REQUISITION_TO_PURCHASE_ORDER"
                ),
                "severity": "HIGH",
                "description": (
                    "Purchase requisitions exceed "
                    "purchase orders, indicating "
                    "requisitions that may not have "
                    "progressed to purchase order "
                    "creation."
                ),
                "affected_records": (
                    total_requisition_count
                    - total_po_count
                ),
                "recommended_action": (
                    "Review pending requisitions "
                    "and identify approval or "
                    "sourcing delays."
                ),
            }
        )

    if (
        total_po_count
        > total_receipt_count
    ):

        bottlenecks.append(
            {
                "stage": (
                    "PURCHASE_ORDER_TO_GOODS_RECEIPT"
                ),
                "severity": "HIGH",
                "description": (
                    "Purchase orders exceed goods "
                    "receipts, indicating orders "
                    "that may be awaiting delivery "
                    "or receipt confirmation."
                ),
                "affected_records": (
                    total_po_count
                    - total_receipt_count
                ),
                "recommended_action": (
                    "Review open purchase orders "
                    "and supplier delivery status."
                ),
            }
        )

    if (
        total_receipt_count
        > total_invoice_count
    ):

        bottlenecks.append(
            {
                "stage": (
                    "GOODS_RECEIPT_TO_INVOICE"
                ),
                "severity": "MEDIUM",
                "description": (
                    "Goods receipts exceed invoices, "
                    "indicating received goods that "
                    "may not yet have corresponding "
                    "supplier invoices."
                ),
                "affected_records": (
                    total_receipt_count
                    - total_invoice_count
                ),
                "recommended_action": (
                    "Review received orders and "
                    "pending supplier invoices."
                ),
            }
        )

    if (
        total_invoice_count
        > total_payment_count
    ):

        bottlenecks.append(
            {
                "stage": "INVOICE_TO_PAYMENT",
                "severity": "HIGH",
                "description": (
                    "Invoices exceed payments, "
                    "indicating invoices that may "
                    "still be awaiting verification "
                    "or payment."
                ),
                "affected_records": (
                    total_invoice_count
                    - total_payment_count
                ),
                "recommended_action": (
                    "Review unpaid invoices and "
                    "identify verification or "
                    "payment processing delays."
                ),
            }
        )

    high_risk_orders = [
        assessment
        for assessment
        in procurement_assessments
        if assessment["risk_level"]
        == "HIGH"
    ]

    escalation_orders = [
        assessment
        for assessment
        in procurement_assessments
        if assessment["approval_route"]
        == "ESCALATION"
    ]

    exceptions = []

    for assessment in high_risk_orders:

        exceptions.append(
            {
                "purchase_order_id": (
                    assessment[
                        "purchase_order_id"
                    ]
                ),
                "exception_type": (
                    "HIGH_PROCUREMENT_RISK"
                ),
                "severity": "HIGH",
                "description": (
                    "Purchase order has been "
                    "classified as HIGH risk."
                ),
                "risk_level": assessment[
                    "risk_level"
                ],
                "recommended_action": (
                    "Perform preventive review "
                    "before execution."
                ),
            }
        )

    for assessment in escalation_orders:

        already_exists = any(
            exception[
                "purchase_order_id"
            ]
            == assessment[
                "purchase_order_id"
            ]
            and exception[
                "exception_type"
            ]
            == "HIGH_PROCUREMENT_RISK"
            for exception in exceptions
        )

        if not already_exists:

            exceptions.append(
                {
                    "purchase_order_id": (
                        assessment[
                            "purchase_order_id"
                        ]
                    ),
                    "exception_type": (
                        "APPROVAL_ESCALATION"
                    ),
                    "severity": "HIGH",
                    "description": (
                        "Purchase order requires "
                        "escalation for additional "
                        "approval."
                    ),
                    "risk_level": assessment[
                        "risk_level"
                    ],
                    "recommended_action": (
                        "Route transaction to the "
                        "required approval authority."
                    ),
                }
            )

    exception_summary = {
        "total_exceptions": len(
            exceptions
        ),
        "high_severity": len(
            [
                exception
                for exception in exceptions
                if exception["severity"]
                == "HIGH"
            ]
        ),
        "medium_severity": len(
            [
                exception
                for exception in exceptions
                if exception["severity"]
                == "MEDIUM"
            ]
        ),
    }

    event_log = _build_event_log(
        process_events
    )

    activity_frequency = (
        _calculate_activity_frequency(
            event_log
        )
    )

    directly_follows = (
        _calculate_directly_follows(
            event_log
        )
    )

    start_end_activities = (
        _calculate_start_end_activities(
            event_log
        )
    )

    cycle_time = (
        _calculate_case_durations(
            event_log
        )
    )

    process_bottlenecks = (
        _detect_process_bottlenecks(
            event_log
        )
    )

    process_variants = (
        _calculate_process_variants(
            event_log
        )
    )

    pm4py_analysis = (
        _run_pm4py_analysis(
            event_log
        )
    )

    celonis_event_log = (
        _build_celonis_event_log(
            event_log
        )
    )

    celonis_metadata = (
        _build_celonis_integration_metadata(
            event_log
        )
    )

    return {
        "overview": {
            "suppliers": (
                total_supplier_count
            ),
            "products": (
                total_product_count
            ),
            "purchase_requisitions": (
                total_requisition_count
            ),
            "purchase_orders": (
                total_po_count
            ),
            "purchase_order_items": (
                len(purchase_order_items)
            ),
            "goods_receipts": (
                total_receipt_count
            ),
            "invoices": (
                total_invoice_count
            ),
            "payments": (
                total_payment_count
            ),
            "process_events": (
                total_event_count
            ),
            "total_purchase_order_value": (
                total_po_value
            ),
            "total_payment_value": (
                total_payment_value
            ),
            "average_purchase_order_value": (
                average_po_value
            ),
        },

        "supplier_intelligence": {
            "average_reliability": (
                average_supplier_reliability
            ),
            "high_risk_suppliers": len(
                high_risk_suppliers
            ),
            "medium_risk_suppliers": len(
                medium_risk_suppliers
            ),
            "reliable_suppliers": len(
                reliable_suppliers
            ),
            "top_suppliers_by_spend": (
                supplier_spend[:5]
            ),
        },

        "procurement_intelligence": {
            "complexity_distribution": (
                complexity_distribution
            ),
            "risk_distribution": (
                risk_distribution
            ),
            "approval_route_distribution": (
                approval_route_distribution
            ),
            "high_value_orders": (
                high_value_orders
            ),
        },

        "process_flow": process_flow,

        "bottlenecks": bottlenecks,

        "process_mining": {
            "engine": (
                "PM4Py"
                if PM4PY_AVAILABLE
                else "PM4Py_NOT_INSTALLED"
            ),
            "event_count": len(
                event_log
            ),
            "case_count": len(
                set(
                    event["case_id"]
                    for event in event_log
                )
            ),
            "activity_frequency": (
                activity_frequency
            ),
            "directly_follows": (
                directly_follows
            ),
            "start_activities": (
                start_end_activities[
                    "start_activities"
                ]
            ),
            "end_activities": (
                start_end_activities[
                    "end_activities"
                ]
            ),
            "cycle_time": cycle_time,
            "process_bottlenecks": (
                process_bottlenecks
            ),
            "process_variants": (
                process_variants
            ),
            "pm4py_discovery": (
                pm4py_analysis
            ),
        },

        "celonis": {
            "integration": (
                celonis_metadata
            ),
            "event_log": (
                celonis_event_log
            ),
        },

        "exceptions": {
            "summary": exception_summary,
            "items": exceptions,
        },
    }