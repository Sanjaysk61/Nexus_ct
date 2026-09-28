from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

EVENT_LOG_PATH = (
    BASE_DIR
    / "data"
    / "event_logs"
    / "process_events.csv"
)


REQUIRED_COLUMNS = [
    "case_id",
    "event_id",
    "activity",
    "timestamp",
    "resource_id",
]


def validate_event_log():
    print("=" * 60)
    print("NEXUS PROCESS EVENT LOG VALIDATION")
    print("=" * 60)

    if not EVENT_LOG_PATH.exists():
        raise FileNotFoundError(
            f"Event log not found: {EVENT_LOG_PATH}"
        )

    df = pd.read_csv(EVENT_LOG_PATH)

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print("\nRequired columns: PASS")

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    if df["timestamp"].isna().any():
        raise ValueError(
            "Invalid timestamps detected."
        )

    print("Timestamp validation: PASS")

    duplicate_events = df["event_id"].duplicated().sum()

    if duplicate_events > 0:
        raise ValueError(
            f"Duplicate event IDs: {duplicate_events}"
        )

    print("Event ID uniqueness: PASS")

    missing_values = df[
        REQUIRED_COLUMNS
    ].isna().sum()

    if missing_values.any():
        print("\nMissing values:")
        print(
            missing_values[
                missing_values > 0
            ]
        )

    else:
        print(
            "Required-field completeness: PASS"
        )

    case_count = df["case_id"].nunique()
    activity_count = df["activity"].nunique()

    print(f"\nUnique cases: {case_count:,}")
    print(f"Unique activities: {activity_count}")

    print("\nActivities:")
    print(
        df["activity"]
        .value_counts()
        .to_string()
    )

    print("\nSample events:")
    print(
        df[
            [
                "case_id",
                "event_id",
                "activity",
                "timestamp",
                "resource_id",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    validate_event_log()