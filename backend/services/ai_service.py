import json
import os

from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()


AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2024-10-21",
)
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")


if not AZURE_OPENAI_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY is not configured.")

if not AZURE_OPENAI_ENDPOINT:
    raise ValueError("AZURE_OPENAI_ENDPOINT is not configured.")

if not AZURE_OPENAI_MODEL:
    raise ValueError("AZURE_OPENAI_MODEL is not configured.")


client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
)


def generate_procurement_analysis(procurement_result):
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

    response = client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
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

    response = client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
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

    response = client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
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