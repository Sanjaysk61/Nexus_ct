from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy.orm import Session

from backend.models import ProcessEvent


def get_process_events(db: Session) -> List[ProcessEvent]:
    return (
        db.query(ProcessEvent)
        .order_by(
            ProcessEvent.case_id,
            ProcessEvent.timestamp
        )
        .all()
    )


def build_celonis_event_log(db: Session) -> List[Dict[str, Any]]:
    events = get_process_events(db)

    event_log = []

    for event in events:
        event_log.append(
            {
                "case_id": event.case_id,
                "activity": event.activity,
                "timestamp": event.timestamp.isoformat()
                if isinstance(event.timestamp, datetime)
                else event.timestamp,
                "resource_id": event.resource_id,
                "supplier_id": event.supplier_id,
                "purchase_order_id": event.purchase_order_id,
                "department_id": event.department_id,
                "amount": event.amount,
            }
        )

    return event_log


def build_celonis_dataframe(db: Session) -> pd.DataFrame:
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

    df = pd.DataFrame(event_log)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    df = df.sort_values(
        by=["case_id", "timestamp"]
    ).reset_index(drop=True)

    return df


def generate_celonis_process_summary(
    db: Session
) -> Dict[str, Any]:

    df = build_celonis_dataframe(db)

    if df.empty:
        return {
            "status": "success",
            "total_events": 0,
            "total_cases": 0,
            "total_activities": 0,
            "activity_frequency": {},
            "case_statistics": [],
        }

    activity_frequency = (
        df["activity"]
        .value_counts()
        .to_dict()
    )

    case_statistics = []

    for case_id, case_df in df.groupby("case_id"):

        case_df = case_df.sort_values("timestamp")

        start_time = case_df["timestamp"].min()
        end_time = case_df["timestamp"].max()

        duration_hours = 0

        if pd.notna(start_time) and pd.notna(end_time):
            duration_hours = (
                end_time - start_time
            ).total_seconds() / 3600

        total_amount = (
            case_df["amount"]
            .fillna(0)
            .sum()
        )

        case_statistics.append(
            {
                "case_id": case_id,
                "event_count": len(case_df),
                "duration_hours": round(
                    duration_hours,
                    2
                ),
                "total_amount": float(
                    total_amount
                ),
            }
        )

    return {
        "status": "success",
        "total_events": len(df),
        "total_cases": df["case_id"].nunique(),
        "total_activities": df["activity"].nunique(),
        "activity_frequency": activity_frequency,
        "case_statistics": case_statistics,
    }


def generate_celonis_export_payload(
    db: Session
) -> Dict[str, Any]:

    event_log = build_celonis_event_log(db)

    return {
        "platform": "Celonis",
        "source": "NEXUS",
        "process": "PROCURE_TO_PAY",
        "event_log": event_log,
        "total_events": len(event_log),
    }