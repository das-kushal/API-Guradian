import os
import json
from dotenv import load_dotenv
from google import genai
from utils import extract_json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_with_ai(diff_result, new_spec):

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

    NEW SPEC:
    {json.dumps(new_spec, indent=2)}

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
