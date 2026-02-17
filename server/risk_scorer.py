def calculate_risk_score(diff, ai_analysis):

    score = 0

    score += len(diff["removed_endpoints"]) * 3
    score += len(diff["method_changes"]) * 2

    if ai_analysis.get("risk_level") == "HIGH":
        score += 5
    elif ai_analysis.get("risk_level") == "MEDIUM":
        score += 3

    return min(score, 10)
