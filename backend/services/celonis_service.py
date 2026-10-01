from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import pm4py
from sqlalchemy.orm import Session

from backend.models import ProcessEvent


def get_celonis_status() -> Dict[str, Any]:
    return {
        "status": "AVAILABLE",
        "platform": "Celonis",
        "integration": "NEXUS",
        "process": "PROCURE_TO_PAY",
        "message": "Celonis process intelligence layer is available.",
    }


def get_process_configuration() -> Dict[str, Any]:
    return {
        "process": "PROCURE_TO_PAY",
        "process_name": "Procure to Pay",
        "platform": "Celonis",
        "case_id": "case_id",
        "activity": "activity",
        "timestamp": "timestamp",
        "resource": "resource_id",
        "supplier": "supplier_id",
        "purchase_order": "purchase_order_id",
        "department": "department_id",
        "amount": "amount",
        "stages": [
            "Purchase Requisition",
            "Approval",
            "Purchase Order",
            "Supplier Confirmation",
            "Goods Receipt",
            "Invoice",
            "Invoice Verification",
            "Payment",
        ],
    }


def get_process_events(
    db: Session,
) -> List[ProcessEvent]:
    return (
        db.query(ProcessEvent)
        .order_by(
            ProcessEvent.case_id,
            ProcessEvent.timestamp,
        )
        .all()
    )


def build_celonis_event_log(
    db: Session,
) -> List[Dict[str, Any]]:
    events = get_process_events(db)

    event_log = []

    for event in events:
        event_log.append(
            {
                "case_id": event.case_id,
                "activity": event.activity,
                "timestamp": (
                    event.timestamp.isoformat()
                    if isinstance(
                        event.timestamp,
                        datetime,
                    )
                    else event.timestamp
                ),
                "resource_id": event.resource_id,
                "supplier_id": event.supplier_id,
                "purchase_order_id": (
                    event.purchase_order_id
                ),
                "department_id": event.department_id,
                "amount": float(
                    event.amount or 0
                ),
            }
        )

    return event_log


def build_celonis_dataframe(
    db: Session,
) -> pd.DataFrame:
    event_log = build_celonis_event_log(db)

    if not event_log:
        return pd.DataFrame(
            columns=[
                "case_id",
                "activity",
                "timestamp",
                "resource_id",
                "supplier_id",
                "purchase_order_id",
                "department_id",
                "amount",
            ]
        )

    dataframe = pd.DataFrame(event_log)

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
    )

    dataframe["amount"] = pd.to_numeric(
        dataframe["amount"],
        errors="coerce",
    ).fillna(0)

    dataframe = dataframe.dropna(
        subset=[
            "case_id",
            "activity",
            "timestamp",
        ]
    )

    dataframe = dataframe.sort_values(
        by=[
            "case_id",
            "timestamp",
        ]
    ).reset_index(drop=True)

    return dataframe


def generate_celonis_process_summary(
    db: Session,
) -> Dict[str, Any]:
    dataframe = build_celonis_dataframe(db)

    if dataframe.empty:
        return {
            "status": "NO_PROCESS_DATA",
            "total_events": 0,
            "total_cases": 0,
            "total_activities": 0,
            "activity_frequency": [],
            "case_statistics": [],
        }

    activity_frequency = (
        dataframe["activity"]
        .value_counts()
        .reset_index()
    )

    activity_frequency.columns = [
        "activity",
        "event_count",
    ]

    case_statistics = (
        dataframe.groupby("case_id")
        .agg(
            event_count=(
                "activity",
                "count",
            ),
            start_time=(
                "timestamp",
                "min",
            ),
            end_time=(
                "timestamp",
                "max",
            ),
            total_amount=(
                "amount",
                "sum",
            ),
        )
        .reset_index()
    )

    case_statistics["duration_hours"] = (
        (
            case_statistics["end_time"]
            - case_statistics["start_time"]
        ).dt.total_seconds()
        / 3600
    ).round(2)

    activity_frequency_records = (
        activity_frequency.to_dict(
            orient="records"
        )
    )

    case_statistics_records = []

    for record in case_statistics.to_dict(
        orient="records"
    ):
        start_time = record.get(
            "start_time"
        )

        end_time = record.get(
            "end_time"
        )

        case_statistics_records.append(
            {
                "case_id": record.get(
                    "case_id"
                ),
                "event_count": int(
                    record.get(
                        "event_count",
                        0,
                    )
                ),
                "start_time": (
                    start_time.isoformat()
                    if hasattr(
                        start_time,
                        "isoformat",
                    )
                    else None
                ),
                "end_time": (
                    end_time.isoformat()
                    if hasattr(
                        end_time,
                        "isoformat",
                    )
                    else None
                ),
                "duration_hours": float(
                    record.get(
                        "duration_hours",
                        0,
                    )
                ),
                "total_amount": float(
                    record.get(
                        "total_amount",
                        0,
                    )
                ),
            }
        )

    return {
        "status": "PROCESS_DATA_AVAILABLE",
        "total_events": int(
            len(dataframe)
        ),
        "total_cases": int(
            dataframe["case_id"]
            .nunique()
        ),
        "total_activities": int(
            dataframe["activity"]
            .nunique()
        ),
        "activity_frequency": (
            activity_frequency_records
        ),
        "case_statistics": (
            case_statistics_records
        ),
    }


def generate_pm4py_process_model(
    db: Session,
) -> Dict[str, Any]:
    dataframe = build_celonis_dataframe(db)

    if dataframe.empty:
        return {
            "status": "NO_PROCESS_DATA",
            "process_model": None,
            "activities": [],
            "transitions": [],
        }

    pm4py_dataframe = dataframe[
        [
            "case_id",
            "activity",
            "timestamp",
        ]
    ].copy()

    pm4py_dataframe = pm4py_dataframe.rename(
        columns={
            "case_id": "case:concept:name",
            "activity": "concept:name",
            "timestamp": "time:timestamp",
        }
    )

    try:
        event_log = pm4py.format_dataframe(
            pm4py_dataframe,
            case_id="case:concept:name",
            activity_key="concept:name",
            timestamp_key="time:timestamp",
        )

        process_tree = (
            pm4py.discover_process_tree_inductive(
                event_log
            )
        )

        activities = sorted(
            event_log[
                "concept:name"
            ].dropna()
            .unique()
            .tolist()
        )

        transitions = []

        for case_id, case_events in event_log.groupby(
            "case:concept:name"
        ):
            case_events = case_events.sort_values(
                "time:timestamp"
            )

            activities_in_case = (
                case_events[
                    "concept:name"
                ]
                .tolist()
            )

            for index in range(
                len(activities_in_case) - 1
            ):
                transitions.append(
                    {
                        "case_id": case_id,
                        "from_activity": (
                            activities_in_case[
                                index
                            ]
                        ),
                        "to_activity": (
                            activities_in_case[
                                index + 1
                            ]
                        ),
                    }
                )

        transition_counts = {}

        for transition in transitions:
            key = (
                transition["from_activity"],
                transition["to_activity"],
            )

            transition_counts[key] = (
                transition_counts.get(
                    key,
                    0,
                )
                + 1
            )

        transition_records = []

        for (
            from_activity,
            to_activity,
        ), count in transition_counts.items():
            transition_records.append(
                {
                    "from_activity": (
                        from_activity
                    ),
                    "to_activity": (
                        to_activity
                    ),
                    "frequency": count,
                }
            )

        transition_records.sort(
            key=lambda item: item[
                "frequency"
            ],
            reverse=True,
        )

        return {
            "status": "PROCESS_MODEL_DISCOVERED",
            "process_model": (
                str(process_tree)
            ),
            "activities": activities,
            "transitions": transition_records,
        }

    except Exception as error:
        return {
            "status": "PROCESS_MODEL_DISCOVERY_FAILED",
            "process_model": None,
            "activities": [],
            "transitions": [],
            "error": str(error),
        }


def generate_process_mining_insights(
    db: Session,
) -> Dict[str, Any]:
    dataframe = build_celonis_dataframe(db)

    if dataframe.empty:
        return {
            "status": "NO_PROCESS_DATA",
            "bottlenecks": [],
            "frequent_paths": [],
            "case_duration": {
                "average_hours": 0,
                "maximum_hours": 0,
                "minimum_hours": 0,
            },
        }

    case_durations = (
        dataframe.groupby("case_id")
        .agg(
            start_time=(
                "timestamp",
                "min",
            ),
            end_time=(
                "timestamp",
                "max",
            ),
        )
    )

    case_durations[
        "duration_hours"
    ] = (
        (
            case_durations["end_time"]
            - case_durations["start_time"]
        )
        .dt.total_seconds()
        / 3600
    )

    average_duration = float(
        case_durations[
            "duration_hours"
        ].mean()
    )

    maximum_duration = float(
        case_durations[
            "duration_hours"
        ].max()
    )

    minimum_duration = float(
        case_durations[
            "duration_hours"
        ].min()
    )

    transitions = []

    for case_id, case_events in dataframe.groupby(
        "case_id"
    ):
        case_events = case_events.sort_values(
            "timestamp"
        )

        activities = case_events[
            "activity"
        ].tolist()

        for index in range(
            len(activities) - 1
        ):
            transitions.append(
                {
                    "case_id": case_id,
                    "from_activity": (
                        activities[index]
                    ),
                    "to_activity": (
                        activities[index + 1]
                    ),
                }
            )

    transition_dataframe = pd.DataFrame(
        transitions
    )

    bottlenecks = []

    if not transition_dataframe.empty:
        transition_frequency = (
            transition_dataframe.groupby(
                [
                    "from_activity",
                    "to_activity",
                ]
            )
            .size()
            .reset_index(
                name="frequency"
            )
            .sort_values(
                "frequency",
                ascending=False,
            )
        )

        for record in transition_frequency.head(
            10
        ).to_dict(
            orient="records"
        ):
            bottlenecks.append(
                {
                    "from_activity": (
                        record[
                            "from_activity"
                        ]
                    ),
                    "to_activity": (
                        record[
                            "to_activity"
                        ]
                    ),
                    "frequency": int(
                        record[
                            "frequency"
                        ]
                    ),
                }
            )

    activity_frequency = (
        dataframe["activity"]
        .value_counts()
        .reset_index()
    )

    activity_frequency.columns = [
        "activity",
        "frequency",
    ]

    frequent_paths = []

    for record in activity_frequency.head(
        10
    ).to_dict(
        orient="records"
    ):
        frequent_paths.append(
            {
                "activity": record[
                    "activity"
                ],
                "frequency": int(
                    record[
                        "frequency"
                    ]
                ),
            }
        )

    return {
        "status": "PROCESS_MINING_ANALYSIS_AVAILABLE",
        "bottlenecks": bottlenecks,
        "frequent_paths": frequent_paths,
        "case_duration": {
            "average_hours": round(
                average_duration,
                2,
            ),
            "maximum_hours": round(
                maximum_duration,
                2,
            ),
            "minimum_hours": round(
                minimum_duration,
                2,
            ),
        },
    }


def generate_celonis_export_payload(
    db: Session,
) -> Dict[str, Any]:
    dataframe = build_celonis_dataframe(db)

    records = []

    for record in dataframe.to_dict(
        orient="records"
    ):
        timestamp = record.get(
            "timestamp"
        )

        records.append(
            {
                "case_id": record.get(
                    "case_id"
                ),
                "activity": record.get(
                    "activity"
                ),
                "timestamp": (
                    timestamp.isoformat()
                    if hasattr(
                        timestamp,
                        "isoformat",
                    )
                    else timestamp
                ),
                "resource_id": record.get(
                    "resource_id"
                ),
                "supplier_id": record.get(
                    "supplier_id"
                ),
                "purchase_order_id": (
                    record.get(
                        "purchase_order_id"
                    )
                ),
                "department_id": record.get(
                    "department_id"
                ),
                "amount": float(
                    record.get(
                        "amount",
                        0,
                    )
                ),
            }
        )

    return {
        "platform": "Celonis",
        "source": "NEXUS",
        "process": "PROCURE_TO_PAY",
        "event_log": records,
        "total_events": len(records),
    }