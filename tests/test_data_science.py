"""
Unit & Integration Tests for NEXUS Data Science Modules
-------------------------------------------------------
Verifies Cycle Time Analytics, Conformance Mining, and Predictive Lead Time ML.
"""

from pathlib import Path
import pytest
import pandas as pd

from process_intelligence.cycle_time_analytics import CycleTimeAnalytics
from process_intelligence.conformance_mining import ConformanceMining
from process_intelligence.predictive_models import DelayPredictionModel

BASE_DIR = Path(__file__).resolve().parents[1]
EVENT_LOG_PATH = BASE_DIR / "data" / "event_logs" / "process_events.csv"


def test_cycle_time_analytics_initialization():
    cta = CycleTimeAnalytics(event_log_path=EVENT_LOG_PATH)
    assert cta.df is not None
    assert len(cta.df) > 0


def test_cycle_time_case_durations():
    cta = CycleTimeAnalytics(event_log_path=EVENT_LOG_PATH)
    case_durations = cta.compute_case_durations()

    assert "case_id" in case_durations.columns
    assert "duration_hours" in case_durations.columns
    assert "duration_days" in case_durations.columns
    assert len(case_durations) > 0
    # Durations should be non-negative
    assert (case_durations["duration_hours"] >= 0).all()


def test_cycle_time_transition_statistics():
    cta = CycleTimeAnalytics(event_log_path=EVENT_LOG_PATH)
    transitions = cta.compute_transition_statistics()

    assert len(transitions) > 0
    for key, stats in transitions.items():
        assert "p50_hours" in stats
        assert "p90_hours" in stats
        assert "p99_hours" in stats
        assert stats["p50_hours"] <= stats["p90_hours"] <= stats["p99_hours"]
        assert stats["count"] > 0


def test_cycle_time_bottlenecks():
    cta = CycleTimeAnalytics(event_log_path=EVENT_LOG_PATH)
    bottlenecks = cta.identify_bottlenecks(top_n=3)

    assert len(bottlenecks) <= 3
    assert len(bottlenecks) > 0
    assert "severity_rank" in bottlenecks[0]
    assert "severity_level" in bottlenecks[0]


def test_cycle_time_executive_summary():
    cta = CycleTimeAnalytics(event_log_path=EVENT_LOG_PATH)
    summary = cta.get_executive_summary()

    assert "total_analyzed_cases" in summary
    assert "overall_cycle_time" in summary
    assert "p50_days" in summary["overall_cycle_time"]
    assert "top_bottlenecks" in summary


def test_conformance_mining_variants():
    cm = ConformanceMining(event_log_path=EVENT_LOG_PATH)
    variants = cm.compute_variant_distribution(top_n=5)

    assert len(variants) > 0
    first = variants[0]
    assert "variant_rank" in first
    assert "case_count" in first
    assert "frequency_pct" in first
    assert "pathway" in first
    assert isinstance(first["violations"], list)


def test_conformance_summary():
    cm = ConformanceMining(event_log_path=EVENT_LOG_PATH)
    summary = cm.get_conformance_summary()

    assert "total_analyzed_cases" in summary
    assert "unique_variants_count" in summary
    assert "conformance_rate_pct" in summary
    assert 0.0 <= summary["conformance_rate_pct"] <= 100.0


def test_predictive_model_training_and_inference():
    model = DelayPredictionModel()
    metrics = model.train()

    assert "roc_auc" in metrics
    assert metrics["roc_auc"] >= 0.50
    assert "feature_importances" in metrics
    assert "business_roi" in metrics
    assert "retained_capital_saved_usd" in metrics["business_roi"]

    # Inference test
    pred = model.predict_order_delay(
        total_amount=65000.0,
        reliability_score=0.72,
        promised_lead_days=10.0,
        order_day_of_week=2,
    )

    assert "predicted_delay_probability" in pred
    assert 0.0 <= pred["predicted_delay_probability"] <= 1.0
    assert "risk_category" in pred
    assert "calibrated_confidence" in pred
    assert "requires_planner_intervention" in pred


def test_api_cycle_times_endpoint():
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    response = client.get("/process/cycle-times")
    assert response.status_code == 200
    data = response.json()
    assert "total_analyzed_cases" in data
    assert "overall_cycle_time" in data


def test_api_bottlenecks_endpoint():
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    response = client.get("/process/bottlenecks?top_n=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 3


def test_api_conformance_endpoint():
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    response = client.get("/process/conformance")
    assert response.status_code == 200
    data = response.json()
    assert "conformance_rate_pct" in data


def test_api_predict_delay_endpoint():
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    # PO-00001 was loaded into the database
    response = client.get("/process/predict-delay/PO-00001")
    assert response.status_code == 200
    data = response.json()
    assert "predicted_delay_probability" in data
    assert "calibrated_confidence" in data
    assert data["purchase_order_id"] == "PO-00001"

