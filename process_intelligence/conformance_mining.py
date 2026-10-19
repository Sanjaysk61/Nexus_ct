"""
NEXUS Process Variant Mining & Conformance Sieve
------------------------------------------------
Reconstructs execution pathways, computes variant frequency distributions,
and flags non-conformant process deviations against the P2P reference standard.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_EVENT_LOG_PATH = BASE_DIR / "data" / "event_logs" / "process_events.csv"

STANDARD_HAPPY_PATH: Tuple[str, ...] = (
    "Purchase Requisition Created",
    "Purchase Requisition Approved",
    "Purchase Order Created",
    "Supplier Confirmation",
    "Goods Receipt",
    "Invoice Received",
    "Invoice Verification",
    "Payment",
)


class ConformanceMining:
    """Mining engine for process variants, happy paths, and compliance violations."""

    def __init__(self, df: Optional[pd.DataFrame] = None, event_log_path: Optional[Union[str, Path]] = None):
        if df is not None:
            self.df = df.copy()
        else:
            path = Path(event_log_path or DEFAULT_EVENT_LOG_PATH)
            self.df = pd.read_csv(path)

        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        self.df = self.df.sort_values(by=["case_id", "timestamp"]).reset_index(drop=True)

    def extract_case_variants(self) -> pd.DataFrame:
        """
        Groups events by case_id in chronological order to form sequence pathways.
        Returns a DataFrame mapping case_id to its activity sequence tuple.
        """
        case_paths = (
            self.df.groupby("case_id")["activity"]
            .agg(tuple)
            .reset_index(name="pathway")
        )
        return case_paths

    def audit_case_conformance(self, pathway: Tuple[str, ...]) -> List[str]:
        """
        Audits a single case sequence pathway against enterprise compliance rules.
        Returns a list of violation codes.
        """
        violations = []
        path_list = list(pathway)

        # 1. Check for Maverick Buying (PO created before Requisition Approved)
        if "Purchase Order Created" in path_list:
            po_idx = path_list.index("Purchase Order Created")
            if "Purchase Requisition Approved" in path_list:
                appr_idx = path_list.index("Purchase Requisition Approved")
                if po_idx < appr_idx:
                    violations.append("MAVERICK_BUYING_EARLY_PO")
            else:
                violations.append("UNAPPROVED_PO_DISPATCH")

        # 2. Check for Retroactive PO (Goods Receipt before PO Created)
        if "Goods Receipt" in path_list and "Purchase Order Created" in path_list:
            gr_idx = path_list.index("Goods Receipt")
            po_idx = path_list.index("Purchase Order Created")
            if gr_idx < po_idx:
                violations.append("RETROACTIVE_PO_AFTER_DELIVERY")

        # 3. Check for Approval Loops
        appr_count = path_list.count("Purchase Requisition Approved")
        if appr_count > 1:
            violations.append("REPEATED_APPROVAL_LOOP")

        # 4. Check for Invoice Mismatches
        if "Invoice Mismatch" in path_list:
            violations.append("INVOICE_MISMATCH_DISCREPANCY")

        # 5. Check for Manual Intervention
        if "Manual Intervention" in path_list:
            violations.append("MANUAL_INTERVENTION_REQUIRED")

        # 6. Check for Unverified Payment
        if "Payment" in path_list:
            pay_idx = path_list.index("Payment")
            if "Invoice Verification" in path_list:
                ver_idx = path_list.index("Invoice Verification")
                if pay_idx < ver_idx:
                    violations.append("PAYMENT_BEFORE_INVOICE_VERIFICATION")
            else:
                violations.append("UNVERIFIED_PAYMENT_DISBURSEMENT")

        # 7. Check if perfectly conformant with standard Happy Path
        if pathway == STANDARD_HAPPY_PATH:
            return []

        if not violations:
            violations.append("CUSTOM_VARIANT_DEVIATION")

        return violations

    def compute_variant_distribution(self, top_n: int = 10) -> List[dict]:
        """
        Calculates frequency and cumulative coverage across all distinct pathways.
        """
        case_paths = self.extract_case_variants()
        total_cases = len(case_paths)

        counts = case_paths["pathway"].value_counts().reset_index()
        counts.columns = ["pathway", "case_count"]
        counts["frequency_pct"] = (counts["case_count"] / total_cases) * 100.0
        counts["cumulative_pct"] = counts["frequency_pct"].cumsum()

        variants = []
        for rank, row in counts.head(top_n).iterrows():
            pathway = row["pathway"]
            violations = self.audit_case_conformance(pathway)
            is_happy_path = (pathway == STANDARD_HAPPY_PATH)

            variants.append({
                "variant_rank": rank + 1,
                "is_happy_path": is_happy_path,
                "case_count": int(row["case_count"]),
                "frequency_pct": round(float(row["frequency_pct"]), 2),
                "cumulative_pct": round(float(row["cumulative_pct"]), 2),
                "step_count": len(pathway),
                "pathway": list(pathway),
                "violations": violations,
            })

        return variants

    def get_conformance_summary(self) -> dict:
        """
        Evaluates overall organizational conformance rate across all transactions.
        """
        case_paths = self.extract_case_variants()
        total_cases = len(case_paths)

        conformance_counts = {
            "HAPPY_PATH_CONFORMANT": 0,
            "INVOICE_MISMATCH_DISCREPANCY": 0,
            "MANUAL_INTERVENTION_REQUIRED": 0,
            "REPEATED_APPROVAL_LOOP": 0,
            "MAVERICK_BUYING_EARLY_PO": 0,
            "UNVERIFIED_PAYMENT": 0,
            "OTHER_DEVIATION": 0,
        }

        for pathway in case_paths["pathway"]:
            violations = self.audit_case_conformance(pathway)
            if not violations:
                conformance_counts["HAPPY_PATH_CONFORMANT"] += 1
            else:
                for v in violations:
                    if v in conformance_counts:
                        conformance_counts[v] += 1
                    elif "UNVERIFIED" in v:
                        conformance_counts["UNVERIFIED_PAYMENT"] += 1
                    else:
                        conformance_counts["OTHER_DEVIATION"] += 1

        conformant_cases = conformance_counts["HAPPY_PATH_CONFORMANT"]
        conformance_rate = (conformant_cases / total_cases * 100.0) if total_cases > 0 else 0.0

        return {
            "total_analyzed_cases": total_cases,
            "unique_variants_count": int(case_paths["pathway"].nunique()),
            "conformance_rate_pct": round(conformance_rate, 2),
            "happy_path_case_count": conformant_cases,
            "deviant_case_count": total_cases - conformant_cases,
            "violation_breakdown": conformance_counts,
        }
