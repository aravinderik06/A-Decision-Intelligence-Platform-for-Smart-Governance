def make_decision(
    problem_category,
    severity_score,
    complaint_count,
    affected_population,
    infrastructure_condition
):
    """
    Rule-based Decision Engine for Smart Governance.

    This engine recommends an action.
    It does NOT make the final government decision.
    """

    severity_score = float(severity_score)
    complaint_count = int(complaint_count)
    affected_population = int(affected_population)

    # --------------------------------------------------
    # Determine priority
    # --------------------------------------------------

    if severity_score >= 75:
        priority = "Critical"
    elif severity_score >= 50:
        priority = "High"
    elif severity_score >= 25:
        priority = "Medium"
    else:
        priority = "Low"

    # --------------------------------------------------
    # Determine recommendation
    # --------------------------------------------------

    if severity_score >= 75 and infrastructure_condition == "Poor":

        recommendation = "Immediate intervention"

        reason = (
            f"High severity ({severity_score:.2f}) combined with "
            f"poor infrastructure requires immediate attention."
        )

    elif severity_score >= 50 and affected_population >= 3000:

        recommendation = "Prioritize for intervention"

        reason = (
            f"The problem has high severity ({severity_score:.2f}) "
            f"and affects approximately {affected_population:,} people."
        )

    elif complaint_count >= 40:

        recommendation = "Prioritize field inspection"

        reason = (
            f"The area has a high complaint frequency "
            f"({complaint_count} complaints), requiring verification "
            f"and field assessment."
        )

    elif infrastructure_condition == "Poor":

        recommendation = "Schedule infrastructure assessment"

        reason = (
            "Infrastructure condition is poor and should be assessed "
            "for corrective action."
        )

    else:

        recommendation = "Monitor and review"

        reason = (
            f"Current severity ({severity_score:.2f}) does not require "
            "immediate intervention under the current rules."
        )

    # --------------------------------------------------
    # Category-specific action
    # --------------------------------------------------

    category_actions = {
        "Roads": "Road maintenance/repair assessment",
        "Water Supply": "Water supply inspection and restoration assessment",
        "Drainage": "Drainage inspection and rehabilitation assessment",
        "Waste Management": "Waste collection/service assessment",
        "Healthcare": "Healthcare facility/service assessment",
        "Education": "School infrastructure/service assessment",
        "Street Lighting": "Street-lighting inspection and repair assessment",
        "Other": "Relevant departmental assessment"
    }

    suggested_action = category_actions.get(
        problem_category,
        "Relevant departmental assessment"
    )

    # --------------------------------------------------
    # Final output
    # --------------------------------------------------

    return {
        "problem_category": problem_category,
        "severity_score": round(severity_score, 2),
        "priority": priority,
        "recommendation": recommendation,
        "suggested_action": suggested_action,
        "reason": reason,
        "officer_decision_required": True
    }


# ======================================================
# TEST THE DECISION ENGINE
# ======================================================

if __name__ == "__main__":

    result = make_decision(
        problem_category="Drainage",
        severity_score=82,
        complaint_count=47,
        affected_population=4200,
        infrastructure_condition="Poor"
    )

    print("\nDECISION ENGINE OUTPUT")
    print("-" * 50)

    for key, value in result.items():
        print(f"{key}: {value}")