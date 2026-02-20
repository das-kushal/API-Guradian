"""
Utility functions for JSON extraction and AI output validation.
"""
import re
import json


# Expected schema for AI output
AI_OUTPUT_SCHEMA = {
    "risk_level": {"type": str, "allowed": ["LOW", "MEDIUM", "HIGH"]},
    "pii_fields": {"type": list},
    "breaking_change_explanation": {"type": str},
    "documentation_score": {"type": (int, float), "min": 1, "max": 10},
    "recommendations": {"type": list},
    "executive_summary": {"type": str},
}


def extract_json(text):
    """
    Extract valid JSON from LLM text output.
    Handles markdown code fences, extra text, and common LLM quirks.
    """
    if not text or not isinstance(text, str):
        return {"error": "Empty or invalid response from AI"}

    # Step 1: Strip markdown code fences if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    # Step 2: Try direct parse first (best case)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Step 3: Find the outermost { ... } block
    # Use a bracket-counting approach instead of greedy regex
    start_idx = text.find("{")
    if start_idx == -1:
        return {"error": "No JSON object found in AI response"}

    depth = 0
    end_idx = -1
    in_string = False
    escape_next = False

    for i in range(start_idx, len(text)):
        c = text[i]
        if escape_next:
            escape_next = False
            continue
        if c == "\\":
            escape_next = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end_idx = i
                break

    if end_idx == -1:
        return {"error": "Malformed JSON: unmatched braces"}

    json_str = text[start_idx:end_idx + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}"}


def validate_ai_output(ai_result):
    """
    Validate and sanitize AI output against the expected schema.
    Fixes common issues:
    - Missing fields get defaults
    - Wrong types get coerced or flagged
    - Out-of-range values get clamped
    Returns (validated_result, warnings)
    """
    if not isinstance(ai_result, dict) or "error" in ai_result:
        return ai_result, ["AI returned an error or invalid data"]

    warnings = []
    validated = {}

    # --- risk_level ---
    risk = ai_result.get("risk_level", "").strip().upper()
    # Sometimes AI returns "LOW | MEDIUM | HIGH" literally
    if risk in ("LOW", "MEDIUM", "HIGH"):
        validated["risk_level"] = risk
    else:
        # Try to infer from partial matches
        if "HIGH" in risk:
            validated["risk_level"] = "HIGH"
        elif "MEDIUM" in risk:
            validated["risk_level"] = "MEDIUM"
        elif "LOW" in risk:
            validated["risk_level"] = "LOW"
        else:
            validated["risk_level"] = "MEDIUM"
            warnings.append(f"AI returned invalid risk_level '{risk}', defaulting to MEDIUM")

    # --- pii_fields ---
    pii = ai_result.get("pii_fields", [])
    if isinstance(pii, list):
        validated["pii_fields"] = [str(f) for f in pii]
    elif isinstance(pii, str):
        validated["pii_fields"] = [pii] if pii.strip() else []
        warnings.append("pii_fields was a string, converted to list")
    else:
        validated["pii_fields"] = []
        warnings.append("pii_fields had unexpected type, defaulting to empty list")

    # --- breaking_change_explanation ---
    explanation = ai_result.get("breaking_change_explanation", "")
    validated["breaking_change_explanation"] = str(explanation) if explanation else "No breaking changes identified."

    # --- documentation_score ---
    doc_score = ai_result.get("documentation_score", 5)
    try:
        doc_score = int(doc_score)
        validated["documentation_score"] = max(1, min(doc_score, 10))
    except (ValueError, TypeError):
        validated["documentation_score"] = 5
        warnings.append(f"documentation_score '{doc_score}' was not a number, defaulting to 5")

    # --- recommendations ---
    recs = ai_result.get("recommendations", [])
    if isinstance(recs, list):
        validated["recommendations"] = [str(r) for r in recs if r]
    elif isinstance(recs, str):
        validated["recommendations"] = [recs] if recs.strip() else []
        warnings.append("recommendations was a string, converted to list")
    else:
        validated["recommendations"] = []

    # --- executive_summary ---
    summary = ai_result.get("executive_summary", "")
    validated["executive_summary"] = str(summary) if summary else "No summary provided."

    # --- Flag any extra unexpected fields ---
    expected_keys = set(AI_OUTPUT_SCHEMA.keys())
    extra_keys = set(ai_result.keys()) - expected_keys
    if extra_keys:
        warnings.append(f"AI returned unexpected fields: {extra_keys}")
        # Keep them but mark as unvalidated
        for k in extra_keys:
            validated[k] = ai_result[k]

    return validated, warnings
