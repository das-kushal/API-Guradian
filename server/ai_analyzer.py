"""
AI analyzer using Google Gemini API.
Mirrored improvements from ai_analyzer_local: grounded prompt, validation.
"""
import os
import json
from dotenv import load_dotenv
from google import genai
from utils import extract_json, validate_ai_output

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _build_minimal_spec(new_spec):
    """Extract only what the AI needs from the spec."""
    return {
        "paths": {
            path: {
                method: {
                    "summary": details.get("summary", ""),
                    "parameters": [
                        p.get("name", "") for p in details.get("parameters", [])
                        if isinstance(p, dict)
                    ],
                }
                for method, details in methods.items()
                if isinstance(details, dict)
            }
            for path, methods in new_spec.get("paths", {}).items()
        },
        "schemas": list(new_spec.get("components", {}).get("schemas", {}).keys()),
    }


def analyze_with_ai(diff_result, new_spec):
    minimal_spec = _build_minimal_spec(new_spec)

    # Pre-computed facts to ground the AI
    facts = []
    if diff_result.get("removed_endpoints"):
        facts.append(f"REMOVED ENDPOINTS: {diff_result['removed_endpoints']}")
    if diff_result.get("added_endpoints"):
        facts.append(f"ADDED ENDPOINTS: {diff_result['added_endpoints']}")
    if diff_result.get("method_changes"):
        facts.append(f"METHOD CHANGES: {json.dumps(diff_result['method_changes'])}")
    if diff_result.get("pii_fields_detected"):
        facts.append(f"PII FIELDS ALREADY DETECTED: {diff_result['pii_fields_detected']}")
    if diff_result.get("naming_issues"):
        facts.append(f"NAMING ISSUES DETECTED: {diff_result['naming_issues']}")
    if diff_result.get("missing_descriptions"):
        facts.append(f"MISSING DESCRIPTIONS: {diff_result['missing_descriptions']}")

    facts_str = "\n".join(facts) if facts else "No major changes detected by scanner."

    prompt = f"""You are an API governance analyst. You must base ALL claims on the data below.

RULES:
1. Return ONLY valid JSON — no explanation, no markdown, no commentary.
2. Do NOT invent endpoints, fields, or issues not in the data.
3. risk_level MUST match actual severity from the changes listed below.
4. pii_fields should ONLY list fields identifiable from the schema/paths.
5. recommendations must be specific, referencing actual endpoints.
6. Output must start with {{ and end with }}.

=== AUTOMATED SCAN RESULTS (ground truth) ===
{facts_str}

=== NEW API SPEC (summary) ===
{json.dumps(minimal_spec, indent=2)}

=== FULL DIFF DATA ===
{json.dumps(diff_result, indent=2)}

Return this JSON:

{{
  "risk_level": "LOW or MEDIUM or HIGH",
  "pii_fields": [],
  "breaking_change_explanation": "Explain ONLY actual breaking changes",
  "documentation_score": 5,
  "recommendations": ["specific actionable items"],
  "executive_summary": "2-3 sentence summary"
}}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        parsed = extract_json(response.text)
        if "error" in parsed:
            return parsed

        validated, warnings = validate_ai_output(parsed)
        if warnings:
            validated["_validation_warnings"] = warnings

        return validated

    except Exception as e:
        return {"error": str(e)}
