"""
Narrative Agent: Generates a concise fraud-risk report for a loan application
using the Gemini (OpenAI-compatible) API. The report assesses identity fraud
likelihood, paystub fraud likelihood, and overall application risk with
rationale and a recommendation.

Environment:
- Requires `GEMINI_API_KEY` in .env
- Requires `openai` python package (>=1.0.0)

Usage example:
    from agents.narrative_agent import NarrativeAgent

    agent = NarrativeAgent(model="gemini-1.5-turbo")
    report = agent.generate_report({
        "applicant": {"name": "Jane Doe", "dob": "1990-04-12"},
        "id_verification": {
            "document_type": "Driver License",
            "name_match": True,
            "dob_match": True,
            "address_match": False,
            "flags": ["Address mismatch vs. application"],
        },
        "paystub": {
            "employer": "Acme Corp",
            "gross_pay": 3850.00,
            "net_pay": 2900.00,
            "pay_frequency": "biweekly",
            "ytd_gross": 31200.00,
            "anomalies": ["Inconsistent YTD progression"],
        },
        "external_checks": {
            "ofac_screen": "clear",
            "employment_verification": "pending",
            "credit_file_thin": True,
        },
        "application_context": {
            "loan_amount": 15000,
            "stated_income": 78000,
            "channel": "online",
        },
    })
    print(report)
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict, Union
from dotenv import load_dotenv
from openai import OpenAI


def _load_env_once() -> None:
    """Load environment variables from .env if present."""
    load_dotenv()


class NarrativeAgent:
    """Generates a fraud-risk narrative report using the OpenAI v1 Chat API."""

    def __init__(self, model: str = "gemini-1.5-turbo", temperature: float = 0.2):
        _load_env_once()
        self.model = model
        self.temperature = temperature

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set. Add it to your environment or .env")

        # OpenAI v1 client
        self._client = OpenAI(api_key=api_key)

    def generate_report(self, application: Union[Dict[str, Any], str]) -> str:
        """Generates a concise fraud-risk report from a JSON or dict payload."""
        if isinstance(application, str):
            try:
                json.loads(application)
                app_payload = application
            except json.JSONDecodeError:
                app_payload = json.dumps({"raw_application": application})
        else:
            app_payload = json.dumps(application, default=str)

        system_prompt = (
            "You are a senior consumer lending fraud analyst. "
            "Analyze the provided loan application context to assess: "
            "1) Identity fraud likelihood, 2) Paystub fraud likelihood, "
            "and 3) Overall application risk. Be conservative, evidence-based, "
            "and concise. Express likelihoods as percentages with a one-line rationale. "
            "Call out key risk signals and any mitigating factors. "
            "If information is missing, state assumptions explicitly. "
            "Output a short, structured report suitable for underwriters."
        )

        user_instructions = (
            "Application data (JSON). Use it to produce the report.\n\n"
            f"DATA: {app_payload}"
        )

        # Call the OpenAI Chat Completions API
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_instructions},
            ],
        )

        content = (resp.choices[0].message.content or "").strip()

        # Ensure report has expected sections
        if not any(h in content for h in ["Identity Fraud Risk", "Paystub Fraud Risk", "Overall Application Risk"]):
            content = (
                "Identity Fraud Risk:\n" + content + "\n\n"
                "Paystub Fraud Risk:\n(see analysis above)\n\n"
                "Overall Application Risk:\n(see analysis above)\n"
            )

        return content


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate fraud-risk report for a loan application")
    parser.add_argument("--json", dest="json_str", help="Raw JSON application payload", required=False)
    parser.add_argument("--file", dest="file_path", help="Path to JSON file with application data", required=False)
    parser.add_argument("--model", dest="model", help="Model (default: gemini-1.5-turbo)", default="gemini-1.5-turbo")
    args = parser.parse_args()

    agent = NarrativeAgent(model=args.model)

    if args.json_str:
        payload = args.json_str
    elif args.file_path:
        with open(args.file_path, "r", encoding="utf-8") as f:
            payload = f.read()
    else:
        payload = {
            "applicant": {"name": "Sample Applicant"},
            "id_verification": {"name_match": True, "dob_match": True},
            "paystub": {"employer": "SampleCo", "gross_pay": 4000, "pay_frequency": "biweekly"},
            "external_checks": {"ofac_screen": "clear"},
            "application_context": {"loan_amount": 10000, "channel": "online"},
        }

    report = agent.generate_report(payload)
    print(report)