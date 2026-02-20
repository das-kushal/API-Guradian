"""
Local AI analyzer using Ollama.
Improved with: grounded prompts, output validation, and retry logic.
"""
import requests
import json
from utils import extract_json, validate_ai_output

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"

MAX_RETRIES = 2


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


def build_prompt(diff_result, new_spec):
    """
    Build a grounded prompt that:
    1. Gives the AI the exact diff data as ground truth
    2. Tells it what was already detected deterministically
    3. Asks it to ONLY supplement with insights it can justify from the data
    """
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
        facts.append(f"PII FIELDS ALREADY DETECTED BY SCANNER: {diff_result['pii_fields_detected']}")
    if diff_result.get("naming_issues"):
        facts.append(f"NAMING ISSUES ALREADY DETECTED: {diff_result['naming_issues']}")
    if diff_result.get("missing_descriptions"):
        facts.append(f"MISSING DESCRIPTIONS: {diff_result['missing_descriptions']}")

    facts_str = "\n".join(facts) if facts else "No major changes detected by automated scanner."

    return f"""You are an API governance analyst. You must base ALL claims on the data below.

RULES:
1. Return ONLY valid JSON — no explanation, no markdown, no commentary.
2. Do NOT invent endpoints, fields, or issues not present in the data.
3. Your risk_level MUST match the severity of actual changes listed below.
4. pii_fields should ONLY contain fields you can identify from the schema/paths below.
5. recommendations must be specific and actionable, referencing actual endpoints.
6. Output must start with {{ and end with }}.

=== AUTOMATED SCAN RESULTS (ground truth) ===
{facts_str}

=== NEW API SPEC (summary) ===
{json.dumps(minimal_spec, indent=2)}

=== FULL DIFF DATA ===
{json.dumps(diff_result, indent=2)}

Based ONLY on the above data, return this JSON:

{{
  "risk_level": "LOW or MEDIUM or HIGH",
  "pii_fields": [],
  "breaking_change_explanation": "Explain ONLY actual breaking changes from the diff",
  "documentation_score": 5,
  "recommendations": ["specific actionable items referencing real endpoints"],
  "executive_summary": "2-3 sentence summary of actual findings"
}}"""


def analyze_with_ai(diff_result, new_spec):
    """Analyze with Ollama, with validation and retry on malformed output."""
    prompt = build_prompt(diff_result, new_spec)

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
                timeout=120,
            )
            response.raise_for_status()
            raw_text = response.json().get("response", "")
            parsed = extract_json(raw_text)

            if "error" in parsed:
                if attempt < MAX_RETRIES:
                    continue  # Retry on parse failure
                return parsed

            # Validate and sanitize
            validated, warnings = validate_ai_output(parsed)
            if warnings:
                validated["_validation_warnings"] = warnings

            return validated

        except requests.exceptions.Timeout:
            return {"error": "LLM timeout — model may be too slow for this spec size"}

        except Exception as e:
            if attempt < MAX_RETRIES:
                continue
            return {"error": str(e)}

    return {"error": "Failed after all retries"}
