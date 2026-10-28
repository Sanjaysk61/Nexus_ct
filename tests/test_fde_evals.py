"""
Automated Forward Deployed Engineering (FDE) Evaluation & Safety Suite
----------------------------------------------------------------------
Validates:
1. Multi-tenant RBAC boundary isolation (anti-leakage)
2. Grounded RAG citation fidelity & clause precision
3. Database tool-calling execution & 3-way reconciliation
4. Human-in-the-Loop (HITL) action state safety
5. FastAPI Copilot REST endpoints & telemetry
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.rag_service import rag_service
from backend.services.agent_service import agent_service
from backend.database import SessionLocal

client = TestClient(app)


def test_rbac_access_isolation():
    """Verify that a Buyer is strictly denied access to Executive Audit Charters."""
    buyer_res = rag_service.query("What are the executive whistleblower and forensic fraud clauses?", role="buyer")
    assert buyer_res["access_granted"] is False
    assert "RBAC VIOLATION PREVENTED" in buyer_res.get("warning", "")
    assert len(buyer_res["citations"]) == 0
    assert "EXECUTIVE" in buyer_res["synthesis"]


def test_rbac_executive_elevation():
    """Verify that an Executive can access executive governance charters."""
    exec_res = rag_service.query("What are the executive whistleblower and forensic fraud clauses?", role="executive")
    assert exec_res["access_granted"] is True
    assert len(exec_res["citations"]) > 0
    assert any("GOV-AUDIT-2026-EXEC" == c["document_id"] for c in exec_res["citations"])


def test_rag_citation_fidelity():
    """Verify policy questions return grounded contract citations with exact clauses."""
    res = rag_service.query("What are the settlement discount payment terms for Apex Logistics?", role="buyer")
    assert res["access_granted"] is True
    assert len(res["citations"]) > 0
    top = res["citations"][0]
    assert "MSA-APEX-2026" == top["document_id"]
    assert "2/10 Net 30" in top["text"]
    assert top["relevance_score"] > 0.1


def test_agent_tool_po_query():
    """Verify the agent can inspect POs from the enterprise relational database."""
    db = SessionLocal()
    try:
        po_res = agent_service.tool_query_po_details(db, "PO-001")
        assert "purchase_order_id" in po_res
        assert "total_amount" in po_res
        assert "status" in po_res
    finally:
        db.close()


def test_agent_audit_3way_matching():
    """Verify 3-way reconciliation audits PO vs GR vs Invoice with Kent confidence."""
    db = SessionLocal()
    try:
        match_res = agent_service.tool_audit_3way_matching(db, "PO-001")
        assert "purchase_order_id" in match_res
        assert "price_variance" in match_res
        assert "matching_status" in match_res
        assert "kent_confidence" in match_res
    finally:
        db.close()


def test_agent_hitl_action_lifecycle():
    """Verify high-risk actions require human sign-off and transition correctly."""
    db = SessionLocal()
    try:
        # Propose hold
        hold = agent_service.tool_propose_po_hold(db, "PO-001", "7-day supplier SLA breach", "Test_Operator")
        action = hold["action"]
        action_id = action["action_id"]

        assert action["status"] == "PENDING_APPROVAL"
        assert action["purchase_order_id"] == "PO-001"

        # Verify it appears in pending actions list
        pending = agent_service.get_pending_actions()
        assert any(act["action_id"] == action_id for act in pending)

        # Decide: Approve
        decision = agent_service.decide_action(action_id, "APPROVED", "Procurement_Director", "Approved for freeze")
        assert decision["status"] == "SUCCESS"
        assert decision["decision"] == "APPROVED"
        assert decision["action"]["status"] == "APPROVED"

        # Verify it is no longer pending
        pending_after = agent_service.get_pending_actions()
        assert not any(act["action_id"] == action_id for act in pending_after)
    finally:
        db.close()


def test_copilot_chat_endpoint():
    """Verify the FastAPI /api/v1/copilot/chat endpoint returns full telemetry."""
    response = client.post(
        "/api/v1/copilot/chat",
        json={
            "query": "What are payment terms for Apex Logistics?",
            "role": "buyer",
            "operator": "Automated_Test"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response_text" in data
    assert "citations" in data
    assert "telemetry" in data
    assert "latency_ms" in data["telemetry"]
    assert data["telemetry"]["confidence_calibration"].startswith("Sherman Kent")
