import os
import json
from dotenv import load_dotenv
from google import genai
from utils import extract_json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_with_ai(diff_result, new_spec):

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

    prompt = f"""
    You are a senior API governance architect in a regulated financial institution.

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
      "documentation_score": 1-10,
      "recommendations": [],
      "executive_summary": ""
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    return extract_json(response.text)
