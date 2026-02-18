import requests
import json
from utils import extract_json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"


def build_prompt(diff_result, new_spec):
    """Build the prompt string. Exposed separately so streaming can reuse it."""
    # Only send what the AI needs — not the full spec
    minimal_spec = {
        "paths": {
            path: {
                method: {"summary": details.get("summary", ""), "parameters": details.get("parameters", [])}
                for method, details in methods.items()
                if isinstance(details, dict)
            }
            for path, methods in new_spec.get("paths", {}).items()
        },
        "schemas": new_spec.get("components", {}).get("schemas", {}),
    }

    return f"""You are a senior API governance architect in a regulated financial institution.

IMPORTANT:
Return ONLY valid JSON.
Do NOT explain.
Do NOT repeat input.
Do NOT wrap in markdown.
Output must start with {{ and end with }}.

DIFF RESULT:
{json.dumps(diff_result, indent=2)}

NEW SPEC (paths summary only):
{json.dumps(minimal_spec, indent=2)}

Analyze:
- Backward compatibility risk
- PII exposure
- Naming inconsistencies
- REST anti-patterns
- Missing descriptions

Return STRICT JSON:

{{
  "risk_level": "LOW | MEDIUM | HIGH",
  "pii_fields": [],
  "breaking_change_explanation": "",
  "documentation_score": 1,
  "recommendations": [],
  "executive_summary": ""
}}"""


def analyze_with_ai(diff_result, new_spec):
    prompt = build_prompt(diff_result, new_spec)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=120,
        )

        response.raise_for_status()
        result = response.json()

        return extract_json(result.get("response", ""))

    except requests.exceptions.Timeout:
        return {"error": "LLM timeout"}

    except Exception as e:
        return {"error": str(e)}
