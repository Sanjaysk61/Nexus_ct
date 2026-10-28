# 🏗️ NEXUS Control Tower (NEXUS-CT)
### *Enterprise Forward Deployed Engineering (FDE) Platform for Autonomous Procure-to-Pay (P2P) Intelligence*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Process Mining](https://img.shields.io/badge/Process%20Mining-PM4Py-blue.svg)](https://pm4py.fit.fraunhofer.de/)
[![RAG](https://img.shields.io/badge/RAG-Multi--Tenant%20RBAC-indigo.svg)](backend/services/rag_service.py)
[![Intelligence](https://img.shields.io/badge/Intelligence-Heuer%20ACH%20%7C%20Kent%20CIA-0078D4.svg)](docs/process-intelligence.md)
[![Tests](https://img.shields.io/badge/Tests-19%2F19%20Passing-emerald.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Executive Summary

**NEXUS Control Tower (NEXUS-CT)** is an enterprise-grade **Forward Deployed AI Platform** that transforms enterprise supply-chain and procurement operations into a proactive, calibrated, autonomous process cockpit.

Sitting directly above core ERPs (**SAP S/4HANA, NetSuite, Coupa, Oracle**), NEXUS provides:
1. **Interactive Control Tower Cockpit:** Real-time web UI with live cycle-time bottleneck telemetry and Human-in-the-Loop action gates.
2. **Multi-Tenant Procurement RAG with RBAC:** Ingests Master Service Agreements (MSAs), SLAs, and policies with strict role-based access isolation (`Buyer`, `Manager`, `Executive`).
3. **Agentic Tool-Calling & Action Dispatcher:** Automatically inspects purchase orders, performs 3-way reconciliation, and stages administrative holds with immutable audit logs.
4. **Process Mining Conformance Engine (`PM4Py`):** Quantifies transition latencies (P50, P90, P99) and flags process deviations.
5. **Calibrated Root-Cause Intelligence:** Constrains AI reasoning to **Richards Heuer's Analysis of Competing Hypotheses (ACH)** and **Sherman Kent CIA estimative standards** (*"Almost Certain (90–99%)"*, *"Probable (60–80%)"*).

---

## 🏛️ System Architecture

```
                                  ┌───────────────────────────────────────────────┐
                                  │      NEXUS OPERATOR COCKPIT (Frontend)        │
                                  │  Role Switcher (RBAC) • Live Chat • HITL Card │
                                  └──────────────────────┬────────────────────────┘
                                                         │ HTTP / SSE Stream
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               FASTAPI BACKEND ROUTER                                   │
│  /api/v1/copilot/chat  •  /api/v1/copilot/stream  •  /api/v1/copilot/actions/decide    │
└──────────────┬─────────────────────────────────────────┬───────────────────────────────┘
               │                                         │
               ▼                                         ▼
┌───────────────────────────────┐         ┌──────────────────────────────────────────────┐
│  MULTI-TENANT RAG ENGINE      │         │     AGENTIC TOOL DISPATCHER                  │
│  • RBAC Document Sieve        │         │     • query_po_details(po_id)                │
│  • Grounded Clause Citations  │         │     • audit_3way_matching(po_id)             │
│  • Strict Zero-Leakage Filter │         │     • propose_po_hold(po_id) [HITL Gateway] │
└──────────────┬────────────────┘         └──────────────────────┬───────────────────────┘
               │                                                 │
               ▼                                                 ▼
┌───────────────────────────────┐         ┌──────────────────────────────────────────────┐
│ KNOWLEDGE BASE (JSON / Vector)│         │ ENTERPRISE DATABASE (SQLite / PostgreSQL)    │
│ MSAs, Vendor SLAs, SOP-2026   │         │ Suppliers, POs, Invoices, Goods Receipts     │
└───────────────────────────────┘         └──────────────────────────────────────────────┘
```

---

## 🛡️ Forward Deployed Engineering (FDE) Capabilities

### 1. Role-Based Access Control (RBAC) Procurement RAG
* Multi-tenant search over vendor contracts (e.g. Apex Logistics, Titan Industrial) and enterprise policies.
* **Security Boundary Guarantee:** A user logged in as a `Buyer` is strictly barred from accessing confidential Executive Audit & Fraud Governance charters. Attempts trigger a logged security notice with zero data leakage.

### 2. Autonomous Tool Calling with Human-in-the-Loop (HITL)
* The Copilot executes structured database tools to diagnose 3-way matching discrepancies (PO vs. Goods Receipt vs. Invoice).
* When anomalous delays or price creep require action, the agent stages a **Purchase Order Administrative Hold** with status `PENDING_APPROVAL`, requiring explicit operator sign-off before execution.

### 3. Sherman Kent CIA Probability Calibration
* Eliminates uncalibrated LLM hallucinations by mapping epistemic confidence directly to standardized CIA probability bands:
  - *"Almost Certain (90–99%)"*
  - *"Probable (60–80%)"*
  - *"Chances About Even (40–60%)"*

---

## 🧪 Automated Verification & Evals (19/19 Passing)

NEXUS includes an automated test suite verifying data science algorithms, process mining models, and FDE agent guardrails:

```bash
# Run full test suite
python -m pytest tests/ -v
```

### Verified Test Matrix:
- `tests/test_fde_evals.py` (7 tests):
  - `test_rbac_access_isolation`: Confirms Buyer cannot view executive whistleblower charter.
  - `test_rbac_executive_elevation`: Confirms Executive receives authorized access.
  - `test_rag_citation_fidelity`: Verifies payment terms match exact clause citations (*2/10 Net 30*).
  - `test_agent_tool_po_query`: Validates PO database inspection tool.
  - `test_agent_audit_3way_matching`: Validates 3-way reconciliation and variance calculation.
  - `test_agent_hitl_action_lifecycle`: Validates staging, pending queue, and approval transition.
  - `test_copilot_chat_endpoint`: Tests REST API response format and telemetry latency waterfall.
- `tests/test_data_science.py` (12 tests):
  - Cycle-time P50/P90/P99 latency profiling, bottleneck identification, variant conformance mining, and cost-sensitive delay prediction.

---

## 🚀 Quickstart & Local Setup

### 1. Local Installation
```bash
# Clone the repository
git clone https://github.com/Sanjaysk61/Nexus_ct.git
cd Nexus_ct

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI Control Tower & Cockpit
uvicorn backend.main:app --reload --port 8000
```

- **Interactive Control Tower Cockpit:** Open `http://localhost:8000/` or `http://localhost:8000/cockpit`
- **Swagger REST API Documentation:** `http://localhost:8000/docs`

### 2. Docker Deployment
```bash
# Build and run containerized platform
docker compose up --build
```

---

## 📄 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
