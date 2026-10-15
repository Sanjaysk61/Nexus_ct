from pathlib import Path

import pandas as pd
import pm4py

print("NEXUS: process_analysis.py started")

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

    exception_activities = [
        "Invoice Mismatch",
        "Manual Intervention",
    ]

    exceptions = df[df["activity"].isin(exception_activities)]

    print("\nEXCEPTION ANALYSIS")
    print("=" * 40)

    print("Cases with invoice mismatches:",
          df.loc[
              df["activity"] == "Invoice Mismatch",
              "case_id"
          ].nunique())

    print("Cases with manual intervention:",
          df.loc[
              df["activity"] == "Manual Intervention",
              "case_id"
          ].nunique())

    print("Cases with either exception:",
          exceptions["case_id"].nunique())

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

def analyze_process_variants(df):
    print("\n" + "=" * 60)
    print("PROCESS VARIANT ANALYSIS")
    print("=" * 60)

    # Step 1: Sort events into chronological order within each case.
    df_sorted = df.sort_values(
        ["case_id", "timestamp"]
    )

    # Step 2: Build the ordered activity sequence for each case.
    case_sequences = (
        df_sorted.groupby("case_id")["activity"]
        .agg(list)
    )

    # Step 3: Convert each sequence into a readable string.
    variant_sequences = case_sequences.apply(
        lambda activities: " -> ".join(activities)
    )

    # Step 4: Count how many cases follow each sequence.
    variant_counts = variant_sequences.value_counts()

    # Step 5: Calculate each variant's share of all cases.
    variant_percentages = (
        variant_counts / len(case_sequences) * 100
    )

    # Step 6: Display the results.
    print(f"\nTotal cases: {len(case_sequences):,}")
    print(f"Unique process variants: {len(variant_counts):,}")

    print("\nTop 10 process variants:")
    print("-" * 60)

    for rank, (variant, count) in enumerate(
        variant_counts.head(10).items(),
        start=1
    ):
        percentage = variant_percentages[variant]

        print(f"\nVariant {rank}")
        print(f"Cases: {count:,}")
        print(f"Percentage: {percentage:.2f}%")
        print(f"Sequence: {variant}")

        
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
    print("NEXUS: calling main()")
    main()