from pathlib import Path

import pandas as pd
import pm4py


BASE_DIR = Path(__file__).resolve().parents[1]

EVENT_LOG_PATH = (
    BASE_DIR
    / "data"
    / "event_logs"
    / "process_events.csv"
)


def load_event_log():
    df = pd.read_csv(EVENT_LOG_PATH)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    return df


def prepare_pm4py_log(df):
    log = pm4py.format_dataframe(
        df,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="timestamp",
    )

    return log


def show_process_statistics(df):
    print("=" * 60)
    print("NEXUS PROCESS INTELLIGENCE ANALYSIS")
    print("=" * 60)

    print("\nTotal events:")
    print(f"{len(df):,}")

    print("\nTotal cases:")
    print(f"{df['case_id'].nunique():,}")

    print("\nTotal activities:")
    print(df["activity"].nunique())

    print("\nActivity frequency:")
    print(
        df["activity"]
        .value_counts()
        .to_string()
    )

    print("\nTop suppliers by event volume:")

    print(
        df.groupby("supplier_id")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .to_string()
    )


def discover_process(df):
    print("\n" + "=" * 60)
    print("PROCESS DISCOVERY")
    print("=" * 60)

    log = prepare_pm4py_log(df)

    print("\nRunning PM4Py process discovery...")

    try:
        net, initial_marking, final_marking = (
            pm4py.discover_petri_net_inductive(
                log
            )
        )

        print("Petri net discovery: SUCCESS")

        print(
            f"Places: {len(net.places)}"
        )

        print(
            f"Transitions: {len(net.transitions)}"
        )

        print(
            f"Arcs: {len(net.arcs)}"
        )

    except Exception as exc:
        print(
            "Process discovery failed:"
        )
        print(exc)


def main():
    df = load_event_log()

    show_process_statistics(df)

    discover_process(df)

    print("\nAnalysis completed.")


if __name__ == "__main__":
    main()