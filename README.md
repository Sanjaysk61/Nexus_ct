# 🏗️ NEXUS Control Tower (NEXUS-CT)
### *Autonomous Process Mining & Cognitive Intelligence Platform for Enterprise Procure-to-Pay (P2P)*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Process Mining](https://img.shields.io/badge/Process%20Mining-PM4Py-blue.svg)](https://pm4py.fit.fraunhofer.de/)
[![Intelligence](https://img.shields.io/badge/Intelligence-Azure%20OpenAI%20%7C%20Heuer%20ACH-0078D4.svg?logo=microsoftazure&logoColor=white)](docs/process-intelligence.md)
[![Calibration](https://img.shields.io/badge/Calibration-Sherman%20Kent%20CIA%20Standard-emerald.svg)](docs/process-intelligence.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Executive Summary

**NEXUS Control Tower** is an enterprise-grade procurement intelligence platform that transforms reactive supply-chain operations into proactive, calibrated, autonomous process intelligence.

Sitting as an intelligent cognitive layer above existing ERPs (**SAP S/4HANA, NetSuite, Coupa, Oracle**), NEXUS continuously reconstructs live **Procure-to-Pay (P2P)** event flows, isolates hidden cycle-time bottlenecks, predicts delivery risk using cost-sensitive machine learning, catches 3-way matching and duplicate invoice leakages, and formulates calibrated, human-in-the-loop action plans.

---

## 🚨 The Enterprise Problem

Enterprises spend billions annually on procurement, yet lose **3% to 7% of total procurement spend** to operational friction, invisible delays, and compliance failures:

1. **Cycle-Time Latency:** Requisitions and purchase orders spend **70%+ of total lifecycle time idling in queues** waiting for sign-offs.
2. **Maverick Spend & Split POs:** Orders structured just under authorization limits (e.g. $9,900 to bypass $10,000 threshold) bypass competitive bidding.
3. **Supplier Lead Time Blind Spots:** Planners discover supplier delays only *after* contractual delivery dates have passed.
4. **3-Way Matching Price & Quantity Creep:** Subtle discrepancies between POs, Goods Receipts (GR), and Invoices drain millions in unverified billing.
5. **Duplicate Invoices & Lost Discounts:** Overpayments and missed 2/10 Net 30 early settlement terms directly reduce free cash flow.
6. **Uncalibrated Alarm Fatigue:** Traditional rule engines flood procurement teams with trivial alerts, while uncalibrated LLMs hallucinate explanations.

👉 *For full mathematical details and industry benchmarks, read [`docs/problem-statement-and-solutions.md`](docs/problem-statement-and-solutions.md).*

---

## 💡 The NEXUS Solution

```
┌─────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│  1. Ingestion   │ ──> │  2. Process Mining   │ ──> │  3. Predictive Risk  │
│  ERP Event Logs │     │  PM4Py DFG & Variants│     │  Asymmetric Cost ML  │
└─────────────────┘     └──────────────────────┘     └──────────────────────┘
                                                                 │
┌─────────────────┐     ┌──────────────────────┐                 ▼
│  6. Execution   │ <── │  5. Human Approval   │ <── ┌──────────────────────┐
│  Automated Sync │     │  Audit-Grade Cockpit │     │  4. Calibrated RCA   │
└─────────────────┘     └──────────────────────┘     │  Heuer ACH + Kent CIA│
                                                     └──────────────────────┘
```

* **Process Mining Conformance Engine (`PM4Py`):** Reconstructs actual execution graphs (DFGs), quantifies variant frequencies, and isolates transition latencies (P50, P90, P99).
* **Deterministic Compliance Sieve:** Real-time 3-way reconciliation (PO vs GR vs Invoice), split PO detection, and authorization limit checks.
* **Cost-Sensitive Delay Forecaster:** Machine learning model weighted with an **Asymmetric Error Cost Matrix** (penalizing missed disruptions 10x–25x over false alarms).
* **Calibrated Agentic Root-Cause Analysis (RCA):**
  - **Richards Heuer Analysis of Competing Hypotheses (ACH):** Evaluates competing causes (Supplier Capacity vs Internal Approval vs Carrier Freight) against empirical event evidence.
  - **Sherman Kent Estimative Language:** Constrains AI narratives to CIA-calibrated probability bands (*"Almost Certain (90–99%)"*, *"Probable (60–80%)"*).
* **Human-in-the-Loop (HITL) Governance:** High-impact interventions require human sign-off with tamper-evident audit logging.

---

## 🏛️ System Architecture

```
Nexus_ct/
├── backend/
│   ├── main.py                     # FastAPI application entrypoint
│   ├── database.py                 # SQLAlchemy session & engine
│   ├── models.py                   # 11 normalized enterprise relational schemas
│   ├── routes.py                   # 20+ REST API endpoints
│   └── services/
│       ├── process_intelligence.py # PM4Py graph & cycle-time analytics
│       ├── procurement_engine.py   # Deterministic compliance & risk engine
│       ├── root_cause.py           # Heuer ACH & diagnostic synthesis
│       ├── ai_service.py           # Azure OpenAI / Calibrated agent service
│       ├── action_planner.py       # Prescriptive mitigation plan formulation
│       ├── approval_service.py     # HITL approval workflow state machine
│       ├── execution_service.py    # Automated action execution & ERP webhooks
│       └── audit_service.py        # Append-only immutable audit logging
├── process_intelligence/
│   ├── process_analysis.py         # Standalone process mining analysis scripts
│   └── validate_event_log.py       # Event log schema & data contract validator
├── docs/
│   ├── architecture.md             # Complete system & data pipeline architecture
│   ├── problem-statement-and-solutions.md # Enterprise failure modes & technical solutions
│   ├── process-intelligence.md     # Algorithmic & mathematical specifications
│   ├── data-contract.md            # IEEE XES / PM4Py shared data contract
│   ├── bussiness-process.md        # Detailed P2P lifecycle workflow guide
│   └── monetization-strategy.md    # Commercial model, SaaS tiers & ROI framework
├── tests/                          # Automated Pytest suite
└── requirements.txt                # Python project dependencies
```

👉 *Read the complete technical specification in [`docs/architecture.md`](docs/architecture.md) and [`docs/process-intelligence.md`](docs/process-intelligence.md).*

---

## 💰 Monetization & Commercial Strategy

NEXUS is designed as a high-margin **B2B Enterprise SaaS** platform delivering a proven **>20x ROI** for mid-to-large enterprises:

| Tier | Annual Spend Volume | Price | Target Customer | Key Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Starter** | Up to $50M | **$25,000 / yr** | Mid-market | 5 Core Rules, Variant Mining, Basic ML |
| **Growth** | Up to $250M | **$75,000 / yr** | Mid-to-Large Enterprise | Full PM4Py DFG, Cost-Sensitive ML, Calibrated RCA |
| **Enterprise** | Unlimited | **$180,000+ / yr** | Global Conglomerates | Dedicated VPC/Air-Gapped, Bi-directional ERP Sync, Custom SLAs |

### Additional Commercial Vectors:
* **Gain-Share Performance Pricing:** 10%–15% contingency fee on verified duplicate invoices and recovered discounts.
* **Supplier Network Passport:** Fast-track pre-cleared payment verification for verified suppliers.
* **ERP Certified Marketplace Connectors:** Turnkey integrations for SAP S/4HANA, NetSuite, and Coupa.

👉 *For the complete financial model and go-to-market plan, see [`docs/monetization-strategy.md`](docs/monetization-strategy.md).*

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Sanjaysk61/Nexus_ct.git
cd Nexus_ct

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Backend API Server
```bash
uvicorn backend.main:app --reload --port 8000
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- Redoc API Specification: `http://localhost:8000/redoc`

### 4. Run Test Suite
```bash
pytest tests/ -v
```

---

## 📜 Documentation Index

* 📘 [Problem Statement & Engineered Solutions](docs/problem-statement-and-solutions.md)
* 📐 [System Architecture Specification](docs/architecture.md)
* 🔬 [Process Intelligence & Algorithmic Specification](docs/process-intelligence.md)
* 📋 [Enterprise Data Contract](docs/data-contract.md)
* 🔄 [P2P Business Process Guide](docs/bussiness-process.md)
* 💼 [Monetization Strategy & Commercial Roadmap](docs/monetization-strategy.md)

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
