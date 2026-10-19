"""
NEXUS Cycle Time & Bottleneck Telemetry Analyzer
------------------------------------------------
Calculates transition durations, statistical percentiles (P50, P90, P99),
bottleneck ranking, and end-to-end P2P journey latency from event logs.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_EVENT_LOG_PATH = BASE_DIR / "data" / "event_logs" / "process_events.csv"


class CycleTimeAnalytics:
    """Enterprise cycle-time telemetry and bottleneck profiling engine."""

    def __init__(self, df: Optional[pd.DataFrame] = None, event_log_path: Optional[Union[str, Path]] = None):
        if df is not None:
            self.df = df.copy()
        else:
            path = Path(event_log_path or DEFAULT_EVENT_LOG_PATH)
            self.df = pd.read_csv(path)

        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        self.df = self.df.sort_values(by=["case_id", "timestamp"]).reset_index(drop=True)

    def compute_case_durations(self) -> pd.DataFrame:
        """Computes total end-to-end cycle time per case (first to last event)."""
        grouped = self.df.groupby("case_id").agg(
            start_time=("timestamp", "min"),
            end_time=("timestamp", "max"),
            event_count=("event_id", "count"),
            supplier_id=("supplier_id", "first"),
            department_id=("department_id", "first"),
            total_amount=("amount", "first"),
        )
        grouped["duration_hours"] = (grouped["end_time"] - grouped["start_time"]).dt.total_seconds() / 3600.0
        grouped["duration_days"] = grouped["duration_hours"] / 24.0
        return grouped.reset_index()

    def compute_transition_statistics(self) -> Dict[str, dict]:
        """
        Computes transition durations between consecutive activities across all cases.
        Returns P50, P90, P99, mean, std, and sample size for each transition pair.
        """
        # Create lead/lag transitions within each case
        df_transitions = self.df.copy()
        df_transitions["next_activity"] = df_transitions.groupby("case_id")["activity"].shift(-1)
        df_transitions["next_timestamp"] = df_transitions.groupby("case_id")["timestamp"].shift(-1)

        # Drop trailing events with no transition
        valid = df_transitions.dropna(subset=["next_activity", "next_timestamp"]).copy()
        valid["transition_hours"] = (valid["next_timestamp"] - valid["timestamp"]).dt.total_seconds() / 3600.0
        valid["transition_days"] = valid["transition_hours"] / 24.0
        valid["transition_key"] = valid["activity"] + " -> " + valid["next_activity"]

        results = {}
        for key, group in valid.groupby("transition_key"):
            hours = group["transition_hours"].values
            days = group["transition_days"].values

            p50 = float(np.percentile(hours, 50))
            p90 = float(np.percentile(hours, 90))
            p99 = float(np.percentile(hours, 99))

            results[key] = {
                "from_activity": group["activity"].iloc[0],
                "to_activity": group["next_activity"].iloc[0],
                "count": int(len(group)),
                "p50_hours": round(p50, 2),
                "p90_hours": round(p90, 2),
                "p99_hours": round(p99, 2),
                "p50_days": round(p50 / 24.0, 2),
                "p90_days": round(p90 / 24.0, 2),
                "p99_days": round(p99 / 24.0, 2),
                "mean_hours": round(float(np.mean(hours)), 2),
                "std_hours": round(float(np.std(hours)), 2),
                "min_hours": round(float(np.min(hours)), 2),
                "max_hours": round(float(np.max(hours)), 2),
                "tail_variance_hours": round(p99 - p50, 2),
            }

        return results

    def identify_bottlenecks(self, top_n: int = 5) -> List[dict]:
        """
        Ranks process transitions by operational bottleneck severity.
        Ranked primarily by P90 duration and tail variance (P99 - P50).
        """
        transitions = self.compute_transition_statistics()
        ranked = sorted(
            transitions.values(),
            key=lambda x: (x["p90_hours"], x["tail_variance_hours"]),
            reverse=True,
        )

        for rank, item in enumerate(ranked[:top_n], start=1):
            item["severity_rank"] = rank
            if item["p90_days"] > 7:
                item["severity_level"] = "CRITICAL"
            elif item["p90_days"] > 3:
                item["severity_level"] = "HIGH"
            else:
                item["severity_level"] = "MODERATE"

        return ranked[:top_n]

    def compute_funnel_summary(self) -> Dict[str, dict]:
        """
        Calculates case drop-off and conversion rates across standard P2P milestones.
        """
        total_cases = self.df["case_id"].nunique()
        stages = [
            "Purchase Requisition Created",
            "Purchase Requisition Approved",
            "Purchase Order Created",
            "Supplier Confirmation",
            "Goods Receipt",
            "Invoice Received",
            "Invoice Verification",
            "Payment",
        ]

        funnel = {}
        for stage in stages:
            cases_with_stage = self.df[self.df["activity"] == stage]["case_id"].nunique()
            conversion_rate = (cases_with_stage / total_cases * 100.0) if total_cases > 0 else 0.0
            funnel[stage] = {
                "active_cases": cases_with_stage,
                "total_cases": total_cases,
                "conversion_rate_pct": round(conversion_rate, 2),
                "dropoff_cases": total_cases - cases_with_stage,
            }

        return funnel

    def get_executive_summary(self) -> dict:
        """Produces a high-level operational SLA telemetry overview for management."""
        case_durations = self.compute_case_durations()
        transitions = self.compute_transition_statistics()
        bottlenecks = self.identify_bottlenecks(top_n=3)
        funnel = self.compute_funnel_summary()

        total_cases = len(case_durations)
        hours = case_durations["duration_hours"].values

        return {
            "total_analyzed_cases": total_cases,
            "overall_cycle_time": {
                "p50_days": round(float(np.percentile(hours, 50)) / 24.0, 2),
                "p90_days": round(float(np.percentile(hours, 90)) / 24.0, 2),
                "p99_days": round(float(np.percentile(hours, 99)) / 24.0, 2),
                "mean_days": round(float(np.mean(hours)) / 24.0, 2),
                "max_days": round(float(np.max(hours)) / 24.0, 2),
            },
            "top_bottlenecks": bottlenecks,
            "transition_count": len(transitions),
            "funnel_completion_rate_pct": funnel.get("Payment", {}).get("conversion_rate_pct", 0.0),
        }
