

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EVENT_LOG_PATH = PROJECT_ROOT / "data" / "event_logs" / "process_events.csv"

START_ACTIVITY = "Purchase Requisition Created"
END_ACTIVITY = "Payment"

TIMESTAMP_COLUMN = "timestamp"
CASE_COLUMN = "case_id"
ACTIVITY_COLUMN = "activity"
SUPPLIER_COLUMN = "supplier_id"

HOURS_PER_DAY = 24


# ---------------------------------------------------------
# 1. LOAD AND VALIDATE EVENT LOG
# ---------------------------------------------------------

def load_event_log():
    """
    Load and validate the NEXUS process event log.

    Returns:
        pandas.DataFrame: Validated event log.
    """

    if not EVENT_LOG_PATH.exists():
        raise FileNotFoundError(
            f"Event log not found at: {EVENT_LOG_PATH}\n"
            "Check the event-log filename and location."
        )

    df = pd.read_csv(EVENT_LOG_PATH)

    required_columns = {
        CASE_COLUMN,
        ACTIVITY_COLUMN,
        TIMESTAMP_COLUMN,
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Event log is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    df[TIMESTAMP_COLUMN] = pd.to_datetime(
        df[TIMESTAMP_COLUMN],
        errors="coerce",
    )

    invalid_timestamps = df[TIMESTAMP_COLUMN].isna().sum()

    if invalid_timestamps:
        print(
            f"Warning: Excluding {invalid_timestamps} events "
            "with invalid timestamps from duration calculations."
        )

        df = df.dropna(subset=[TIMESTAMP_COLUMN]).copy()

    df[CASE_COLUMN] = df[CASE_COLUMN].astype(str)
    df[ACTIVITY_COLUMN] = df[ACTIVITY_COLUMN].astype(str)

    df = df.sort_values(
        [CASE_COLUMN, TIMESTAMP_COLUMN]
    ).reset_index(drop=True)

    if df.empty:
        raise ValueError("The event log contains no valid events.")

    print("\n" + "=" * 65)
    print("NEXUS CYCLE TIME ANALYSIS")
    print("=" * 65)

    print(f"Event log: {EVENT_LOG_PATH}")
    print(f"Valid events: {len(df):,}")
    print(f"Unique cases: {df[CASE_COLUMN].nunique():,}")
    print(f"Activities: {df[ACTIVITY_COLUMN].nunique():,}")

    return df


# ---------------------------------------------------------
# 2. OVERALL PROCUREMENT CYCLE TIME
# ---------------------------------------------------------

def calculate_overall_cycle_time(df):
    """
    Calculate elapsed time from PR Created to Payment per case.

    Cases missing either endpoint are excluded from the
    overall cycle-time summary.
    """

    print("\n" + "=" * 65)
    print("1. OVERALL PROCUREMENT CYCLE TIME")
    print("=" * 65)

    start_events = (
        df[df[ACTIVITY_COLUMN] == START_ACTIVITY]
        .groupby(CASE_COLUMN)[TIMESTAMP_COLUMN]
        .min()
        .rename("start_time")
    )

    end_events = (
        df[df[ACTIVITY_COLUMN] == END_ACTIVITY]
        .groupby(CASE_COLUMN)[TIMESTAMP_COLUMN]
        .max()
        .rename("end_time")
    )

    cycle_times = pd.concat(
        [start_events, end_events],
        axis=1,
    ).dropna()

    cycle_times["cycle_time_hours"] = (
        cycle_times["end_time"] - cycle_times["start_time"]
    ).dt.total_seconds() / 3600

    negative_cycles = cycle_times["cycle_time_hours"] < 0

    if negative_cycles.any():
        print(
            f"Warning: Excluding {negative_cycles.sum()} cases "
            "with negative overall cycle time."
        )

        cycle_times = cycle_times.loc[~negative_cycles].copy()

    cycle_times["cycle_time_days"] = (
        cycle_times["cycle_time_hours"] / HOURS_PER_DAY
    )

    if cycle_times.empty:
        print(
            "No complete cases contain both PR Created and Payment."
        )

        return cycle_times

    print(f"\nComplete cases: {len(cycle_times):,}")

    print("\nCycle-time statistics:")

    print(
        cycle_times["cycle_time_days"]
        .describe(percentiles=[0.50, 0.90, 0.95])
        .round(2)
        .to_string()
    )

    print("\nStatistics are measured in days.")


    print("\nSlowest 10 cases:")

    slowest_cases = (
        cycle_times[
            ["start_time", "end_time", "cycle_time_days"]
        ]
        .sort_values("cycle_time_days", ascending=False)
        .head(10)
        .copy()
    )

    # Round only the numeric column.
    slowest_cases["cycle_time_days"] = (
        slowest_cases["cycle_time_days"].round(2)
    )

    print(slowest_cases.to_string())

    return cycle_times


# ---------------------------------------------------------
# 3. DURATION BETWEEN CONSECUTIVE ACTIVITIES
# ---------------------------------------------------------

def calculate_stage_durations(df):
    """
    Calculate elapsed time between consecutive events in each case.

    If an activity occurs multiple times within a case, each
    consecutive event transition is retained separately.
    """

    print("\n" + "=" * 65)
    print("2. PROCESS STAGE DURATIONS")
    print("=" * 65)

    events = df.sort_values(
        [CASE_COLUMN, TIMESTAMP_COLUMN]
    ).copy()

    events["next_activity"] = (
        events.groupby(CASE_COLUMN)[ACTIVITY_COLUMN].shift(-1)
    )

    events["next_timestamp"] = (
        events.groupby(CASE_COLUMN)[TIMESTAMP_COLUMN].shift(-1)
    )

    transitions = events.dropna(
        subset=["next_activity", "next_timestamp"]
    ).copy()

    transitions["stage_duration_hours"] = (
        transitions["next_timestamp"] - transitions[TIMESTAMP_COLUMN]
    ).dt.total_seconds() / 3600

    transitions["stage_duration_days"] = (
        transitions["stage_duration_hours"] / HOURS_PER_DAY
    )

    transitions["stage"] = (
        transitions[ACTIVITY_COLUMN]
        + " -> "
        + transitions["next_activity"]
    )

    negative_durations = transitions["stage_duration_hours"] < 0

    if negative_durations.any():
        print(
            f"Warning: Excluding {negative_durations.sum()} "
            "negative-duration transitions."
        )

        transitions = transitions.loc[
            ~negative_durations
        ].copy()

    if transitions.empty:
        print("No valid consecutive activity transitions found.")

        return transitions, pd.DataFrame()

    stage_summary = (
        transitions.groupby("stage")["stage_duration_hours"]
        .agg(
            case_transitions="count",
            average_hours="mean",
            median_hours="median",
            maximum_hours="max",
        )
        .reset_index()
    )

    stage_summary["p90_hours"] = (
        transitions.groupby("stage")["stage_duration_hours"]
        .quantile(0.90)
        .values
    )

    stage_summary = stage_summary.sort_values(
        "median_hours",
        ascending=False,
    )

    print("\nStages ranked by median duration:")

    print(
        stage_summary.round(2).to_string(index=False)
    )

    return transitions, stage_summary


# ---------------------------------------------------------
# 4. BOTTLENECK IDENTIFICATION
# ---------------------------------------------------------

def identify_bottlenecks(stage_summary):
    """
    Rank stages by median and average duration.

    Longer duration indicates a potential bottleneck, not
    proof of the root cause.
    """

    print("\n" + "=" * 65)
    print("3. BOTTLENECK IDENTIFICATION")
    print("=" * 65)

    if stage_summary.empty:
        print("No stage-duration results available.")

        return

    median_ranked = stage_summary.sort_values(
        "median_hours",
        ascending=False,
    )

    print("\nTop 5 stages by median duration:")

    print(
        median_ranked[
            [
                "stage",
                "median_hours",
                "average_hours",
                "p90_hours",
                "case_transitions",
            ]
        ]
        .head(5)
        .round(2)
        .to_string(index=False)
    )

    average_ranked = stage_summary.sort_values(
        "average_hours",
        ascending=False,
    )

    print("\nTop 5 stages by average duration:")

    print(
        average_ranked[
            [
                "stage",
                "average_hours",
                "median_hours",
                "p90_hours",
                "case_transitions",
            ]
        ]
        .head(5)
        .round(2)
        .to_string(index=False)
    )

    print(
        "\nInterpretation: High median duration suggests a "
        "consistently slow stage. A much higher average than "
        "median may indicate a small number of unusually "
        "delayed cases."
    )


# ---------------------------------------------------------
# 5. NORMAL VS. EXCEPTION CASES
# ---------------------------------------------------------

def compare_exception_cycle_times(df, cycle_times):
    """
    Compare overall cycle time for cases with and without
    an Invoice Mismatch event.
    """

    print("\n" + "=" * 65)
    print("4. NORMAL VS. EXCEPTION CASES")
    print("=" * 65)

    if cycle_times.empty:
        print("No complete cycle-time data available.")

        return pd.DataFrame()

    mismatch_cases = set(
        df.loc[
            df[ACTIVITY_COLUMN] == "Invoice Mismatch",
            CASE_COLUMN,
        ]
    )

    comparison = cycle_times.copy()

    comparison["case_type"] = comparison.index.map(
        lambda case_id: (
            "Invoice Mismatch"
            if case_id in mismatch_cases
            else "Normal"
        )
    )

    summary = (
        comparison.groupby("case_type")["cycle_time_days"]
        .agg(
            cases="count",
            average_days="mean",
            median_days="median",
            maximum_days="max",
        )
        .reset_index()
    )

    print("\nCycle-time comparison:")

    print(summary.round(2).to_string(index=False))

    normal = comparison.loc[
        comparison["case_type"] == "Normal",
        "cycle_time_days",
    ]

    exception = comparison.loc[
        comparison["case_type"] == "Invoice Mismatch",
        "cycle_time_days",
    ]

    if not normal.empty and not exception.empty:
        normal_median = normal.median()
        exception_median = exception.median()

        difference = exception_median - normal_median

        print("\nMedian cycle-time difference:")
        print(f"Normal cases:    {normal_median:.2f} days")
        print(f"Mismatch cases:  {exception_median:.2f} days")
        print(f"Difference:      {difference:.2f} days")

        if normal_median > 0:
            percentage = difference / normal_median * 100

            print(
                f"Relative difference: {percentage:.2f}%"
            )

    print(
        "\nNote: This is a descriptive comparison. It does not "
        "prove that invoice mismatches cause longer cycle times."
    )

    return comparison


# ---------------------------------------------------------
# 6. SUPPLIER DELIVERY PERFORMANCE
# ---------------------------------------------------------

def analyze_supplier_delivery(df):
    """
    Compare time between Supplier Confirmation and Goods Receipt.

    Supplier-level analysis requires supplier_id to be present
    in the event log.
    """

    print("\n" + "=" * 65)
    print("5. SUPPLIER DELIVERY PERFORMANCE")
    print("=" * 65)

    if SUPPLIER_COLUMN not in df.columns:
        print(
            f"Cannot calculate supplier delivery performance: "
            f"'{SUPPLIER_COLUMN}' is missing from the event log."
        )

        print(
            "If supplier_id exists in another dataset, merge it "
            "using a reliable case or purchase-order key."
        )

        return pd.DataFrame()

    supplier_events = df[
        df[ACTIVITY_COLUMN].isin(
            ["Supplier Confirmation", "Goods Receipt"]
        )
    ].copy()

    supplier_events[SUPPLIER_COLUMN] = (
        supplier_events[SUPPLIER_COLUMN].fillna("Unknown")
    )

    confirmation = (
        supplier_events[
            supplier_events[ACTIVITY_COLUMN] == "Supplier Confirmation"
        ]
        .groupby(CASE_COLUMN)[TIMESTAMP_COLUMN]
        .min()
        .rename("confirmation_time")
    )

    receipt = (
        supplier_events[
            supplier_events[ACTIVITY_COLUMN] == "Goods Receipt"
        ]
        .groupby(CASE_COLUMN)[TIMESTAMP_COLUMN]
        .min()
        .rename("receipt_time")
    )

    supplier_per_case = (
        supplier_events.groupby(CASE_COLUMN)[SUPPLIER_COLUMN]
        .first()
        .rename(SUPPLIER_COLUMN)
    )

    delivery = pd.concat(
        [confirmation, receipt, supplier_per_case],
        axis=1,
    ).dropna(
        subset=[
            "confirmation_time",
            "receipt_time",
        ]
    )

    delivery["delivery_hours"] = (
        delivery["receipt_time"] - delivery["confirmation_time"]
    ).dt.total_seconds() / 3600

    delivery["delivery_days"] = (
        delivery["delivery_hours"] / HOURS_PER_DAY
    )

    invalid = delivery["delivery_hours"] < 0

    if invalid.any():
        print(
            f"Warning: Excluding {invalid.sum()} cases with "
            "Goods Receipt before Supplier Confirmation."
        )

        delivery = delivery.loc[~invalid].copy()

    if delivery.empty:
        print("No valid supplier delivery durations found.")

        return delivery

    supplier_summary = (
        delivery.groupby(SUPPLIER_COLUMN)["delivery_days"]
        .agg(
            purchase_orders="count",
            average_delivery_days="mean",
            median_delivery_days="median",
            maximum_delivery_days="max",
        )
        .reset_index()
        .sort_values(
            "median_delivery_days",
            ascending=False,
        )
    )

    print("\nSuppliers ranked by median delivery duration:")

    print(
        supplier_summary.head(15).round(2).to_string(index=False)
    )

    print(
        "\nImportant: This measures elapsed time between "
        "confirmation and goods receipt. It is not necessarily "
        "the same as lateness against a contractual due date."
    )

    return supplier_summary


# ---------------------------------------------------------
# 7. SAVE ANALYSIS OUTPUTS
# ---------------------------------------------------------

def save_analysis_outputs(
    cycle_times,
    transitions,
    stage_summary,
    exception_comparison,
    supplier_summary,
):
    """
    Save analysis results to the reports directory.
    """

    output_dir = PROJECT_ROOT / "reports" / "cycle_time"

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    outputs = {
        "overall_cycle_times.csv": cycle_times,
        "stage_transitions.csv": transitions,
        "stage_duration_summary.csv": stage_summary,
        "exception_cycle_time_comparison.csv": exception_comparison,
        "supplier_delivery_performance.csv": supplier_summary,
    }

    print("\n" + "=" * 65)
    print("6. SAVING ANALYSIS OUTPUTS")
    print("=" * 65)

    for filename, dataframe in outputs.items():
        output_path = output_dir / filename

        dataframe.to_csv(
            output_path,
            index=False,
        )

        print(f"Saved: {output_path}")


# ---------------------------------------------------------
# 8. MAIN EXECUTION
# ---------------------------------------------------------

def main():
    df = load_event_log()

    cycle_times = calculate_overall_cycle_time(df)

    transitions, stage_summary = calculate_stage_durations(df)

    identify_bottlenecks(stage_summary)

    exception_comparison = compare_exception_cycle_times(
        df,
        cycle_times,
    )

    supplier_summary = analyze_supplier_delivery(df)

    save_analysis_outputs(
        cycle_times,
        transitions,
        stage_summary,
        exception_comparison,
        supplier_summary,
    )

    print("\n" + "=" * 65)
    print("NEXUS CYCLE TIME ANALYSIS COMPLETED")
    print("=" * 65)


if __name__ == "__main__":
    main()


