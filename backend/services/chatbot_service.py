import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()


AZURE_OPENAI_API_KEY = os.getenv(
    "AZURE_OPENAI_API_KEY"
)

AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT"
)

AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2024-10-21",
)

AZURE_OPENAI_MODEL = os.getenv(
    "AZURE_OPENAI_MODEL"
)


if (
    AZURE_OPENAI_API_KEY
    and AZURE_OPENAI_ENDPOINT
    and AZURE_OPENAI_MODEL
):

    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
    )

else:
    client = None


def generate_nexus_chat_response(
    question: str,
    context: Dict[str, Any],
) -> str:

    if client is None:
        return (
            "NEXUS AI Assistant is not configured. "
            "Please configure the Azure OpenAI "
            "environment variables."
        )

    serialized_context = json.dumps(
        context,
        indent=2,
        default=str,
    )

    prompt = f"""
You are NEXUS AI Assistant.

NEXUS is an AI-powered Procurement Intelligence
and Process Resilience Control Tower.

You assist procurement managers, supply chain
teams, process analysts, and business users.

AVAILABLE NEXUS DATA:

{serialized_context}

USER QUESTION:

{question}

RULES:

1. Use only the supplied NEXUS data.
2. Do not invent transactions.
3. Do not invent suppliers.
4. Do not invent amounts.
5. Do not invent process events.
6. Clearly distinguish deterministic findings,
   ML predictions, process mining findings,
   and AI explanations.
7. Do not override procurement approval rules.
8. Do not approve or reject transactions.
9. If information is unavailable, say so.
10. Give a concise business-friendly answer.

Answer the user's question directly.
"""

    response = client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the NEXUS Procurement "
                    "AI Assistant."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return (
        response.choices[0]
        .message
        .content
    )