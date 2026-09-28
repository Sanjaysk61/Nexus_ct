from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

EVENT_LOG_PATH = (
    BASE_DIR
    / "data"
    / "event_logs"
    / "process_events.csv"
)


def test_event_log_exists():
    assert EVENT_LOG_PATH.exists()


def test_event_log_has_required_columns():
    df = pd.read_csv(EVENT_LOG_PATH)

    required_columns = {
        "case_id",
        "event_id",
        "activity",
        "timestamp",
        "resource_id",
    }

    assert required_columns.issubset(
        df.columns
    )


def test_event_log_has_many_events():
    df = pd.read_csv(EVENT_LOG_PATH)

    assert len(df) >= 50000


def test_event_ids_are_unique():
    df = pd.read_csv(EVENT_LOG_PATH)

    assert df["event_id"].is_unique


def test_cases_exist():
    df = pd.read_csv(EVENT_LOG_PATH)

    assert df["case_id"].nunique() >= 9000