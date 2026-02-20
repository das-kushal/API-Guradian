"""
Hardened risk scorer.
Uses deterministic signals from the enhanced diff engine + AI analysis.
The score is primarily driven by concrete, verifiable facts.
AI analysis adjusts the score only within a bounded range to prevent
hallucinated AI claims from skewing the result.
"""


def calculate_risk_score(diff, ai_analysis):
    """
    Calculate a risk score from 0-10.

    Scoring weights:
    - Removed endpoints:     3 pts each (breaking change)
    - Removed methods:       2 pts each (breaking change)
    - Removed parameters:    1 pt each  (potentially breaking)
    - Removed responses:     1 pt each  (contract change)
    - Schema removals:       2 pts each (breaking)
    - Schema field removals: 1 pt each  (breaking)
    - PII fields detected:   1 pt each  (security risk, max 3)
    - Missing descriptions:  0.5 pt each (governance, max 2)
    - Naming issues:         0.5 pt each (anti-pattern, max 1)
    - AI risk adjustment:    max ±2 pts (bounded to prevent hallucination skew)
    """
    score = 0.0
    breakdown = {}

    # --- Deterministic signals (these are verifiable facts) ---

    # Breaking: removed endpoints
    removed_ep = len(diff.get("removed_endpoints", []))
    score += removed_ep * 3
    breakdown["removed_endpoints"] = removed_ep * 3

    # Breaking: removed methods
    removed_methods_count = sum(
        len(mc.get("removed_methods", []))
        for mc in diff.get("method_changes", [])
    )
    score += removed_methods_count * 2
    breakdown["removed_methods"] = removed_methods_count * 2

    # Potentially breaking: removed parameters
    removed_params_count = sum(
        len(pc.get("removed_params", []))
        for pc in diff.get("parameter_changes", [])
    )
    score += removed_params_count * 1
    breakdown["removed_parameters"] = removed_params_count * 1

    # Contract change: removed responses
    removed_resp_count = sum(
        len(rc.get("removed_responses", []))
        for rc in diff.get("response_changes", [])
    )
    score += removed_resp_count * 1
    breakdown["removed_responses"] = removed_resp_count * 1

    # Schema breaking changes
    schema_changes = diff.get("schema_changes", {})
    removed_schemas = len(schema_changes.get("removed_schemas", []))
    score += removed_schemas * 2
    breakdown["removed_schemas"] = removed_schemas * 2

    removed_fields = sum(
        len(fc.get("removed_fields", []))
        for fc in schema_changes.get("field_changes", [])
    )
    score += removed_fields * 1
    breakdown["removed_fields"] = removed_fields * 1

    # Security: PII exposure (capped at 3 pts)
    pii_count = len(diff.get("pii_fields_detected", []))
    pii_score = min(pii_count * 1, 3)
    score += pii_score
    breakdown["pii_exposure"] = pii_score

    # Governance: missing descriptions (capped at 2 pts)
    missing_desc = len(diff.get("missing_descriptions", []))
    desc_score = min(missing_desc * 0.5, 2)
    score += desc_score
    breakdown["missing_descriptions"] = desc_score

    # Anti-patterns: naming issues (capped at 1 pt)
    naming = len(diff.get("naming_issues", []))
    naming_score = min(naming * 0.5, 1)
    score += naming_score
    breakdown["naming_issues"] = naming_score

    # --- AI adjustment (BOUNDED to prevent hallucination skew) ---
    ai_adjustment = 0
    if isinstance(ai_analysis, dict) and "error" not in ai_analysis:
        risk = ai_analysis.get("risk_level", "").strip().upper()
        if risk == "HIGH":
            ai_adjustment = 2
        elif risk == "MEDIUM":
            ai_adjustment = 1
        elif risk == "LOW":
            ai_adjustment = -1
    
    score += ai_adjustment
    breakdown["ai_adjustment"] = ai_adjustment

    final_score = max(0, min(round(score), 10))

    return {
        "score": final_score,
        "breakdown": breakdown,
        "total_raw": round(score, 1),
    }
