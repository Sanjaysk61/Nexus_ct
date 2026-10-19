import json
import os

from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()


def get_azure_client():
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    if not api_key or not endpoint:
        return None
    return AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=version,
    )


def get_azure_model():
    return os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")



def generate_procurement_analysis(procurement_result):
    client = get_azure_client()
    if client is None:
        risk = procurement_result.get("risk_level", "STANDARD")
        complexity = procurement_result.get("complexity", "NOMINAL")
        route = procurement_result.get("approval_route", "AUTO_APPROVAL")
        val = float(procurement_result.get("purchase_order_value", 0.0) or 0.0)
        return (
            f"[CALIBRATED AI ANALYSIS - SIMULATED MODE] Purchase order evaluated with {risk} risk and "
            f"{complexity} complexity (Total Value: ${val:,.2f}). Recommended route: {route}."
        )

    prompt = f"""
You are the AI analysis engine for NEXUS,
an AI-powered Procurement Intelligence Platform.

Analyze the following procurement assessment:

{procurement_result}

Provide a concise business-oriented analysis.

Focus on:

1. Purchase order value
2. Procurement complexity
3. Supplier reliability and risk
4. Approval route
5. Recommended action
6. Important procurement concerns

Do not invent information that is not present
in the procurement assessment.

Return the analysis as a clear professional paragraph.
"""

    model = get_azure_model()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a procurement intelligence "
                    "assistant for the NEXUS platform."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.choices[0].message.content


def generate_process_intelligence(process_data):
    client = get_azure_client()
    if client is None:
        overview = process_data.get("overview", {})
        pos = overview.get("purchase_orders", 0)
        spend = float(overview.get("total_purchase_order_value", 0.0) or 0.0)
        return (
            f"[CALIBRATED PROCESS INTELLIGENCE - SIMULATED MODE] Analyzed {pos} active purchase orders "
            f"representing ${spend:,.2f} in managed procurement volume. Conformance and SLA metrics remain nominal."
        )

    data = json.dumps(
        process_data,
        indent=2,
        default=str,
    )

    prompt = f"""
You are the Process Intelligence AI engine for NEXUS,
an AI-powered Procurement Intelligence Platform.

Analyze the following structured procurement process data.

DATA:
{data}

Your task is to identify meaningful procurement patterns
and explain them for a business stakeholder.

Focus on:

1. Overall procurement activity
2. Purchase order value and transaction volume
3. Supplier and procurement patterns
4. Risk distribution
5. Procurement complexity
6. Approval and escalation patterns
7. Process bottlenecks or areas requiring attention
8. Important business observations

Use ONLY the information provided in the data.

Do not invent suppliers, transactions, amounts, risks,
dates, or business facts.

Do not make decisions on behalf of management.

Return a clear professional business analysis in 3 to 5
short paragraphs.

Do not use markdown tables.
Do not return JSON.
"""

    model = get_azure_model()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Process Intelligence analyst "
                    "for the NEXUS procurement platform."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.choices[0].message.content


def generate_root_cause_explanation(root_cause_result):
    client = get_azure_client()
    if client is None:
        risk = root_cause_result.get("risk_level", "EVALUATING")
        causes = root_cause_result.get("root_causes", ["Baseline Lead Time Volatility"])
        rec = root_cause_result.get("recommended_action", "Proceed with standard procurement monitoring")
        causes_str = ", ".join(causes) if isinstance(causes, list) else str(causes)
        return (
            f"[CALIBRATED ROOT CAUSE NARRATIVE - SIMULATED MODE] Evaluated risk status: {risk}. "
            f"Primary identified factors: {causes_str}. Recommended mitigation: {rec}."
        )

    data = json.dumps(
        root_cause_result,
        indent=2,
        default=str,
    )

    prompt = f"""
You are the Root Cause Intelligence AI engine for NEXUS.

Analyze the structured root cause assessment below.

DATA:
{data}

Explain the procurement situation for a business stakeholder.

Focus on:

1. What caused the elevated risk
2. Which factors are contributing to the risk
3. Why the recommended action was generated
4. What the human reviewer should pay attention to

Use ONLY the information provided.

Do not invent facts, suppliers, amounts, risks,
transactions, or business events.

Do not change the risk level.
Do not change the identified root causes.
Do not create a different recommendation.

The deterministic NEXUS engine is the source of truth.

Return 2 to 4 concise professional paragraphs.

Do not use markdown tables.
Do not return JSON.
"""

    model = get_azure_model()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Root Cause Intelligence analyst "
                    "for the NEXUS procurement platform."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.choices[0].message.content