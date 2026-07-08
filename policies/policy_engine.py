def decide_action(risk):

    score = risk["score"]

    technique_count = risk.get(
        "technique_count",
        0
    )

    summary = risk.get(
        "summary",
        {}
    )

    critical_hits = summary.get(
        "critical",
        0
    )


    # -----------------------
    # BLOCK
    # -----------------------

    if score >= 100:

        return {
            "decision": "BLOCK",
            "reason": "critical_score"
        }


    if critical_hits > 0:

        return {
            "decision": "BLOCK",
            "reason": "critical_detection"
        }


    if (
        score >= 70
        and technique_count >= 3
    ):

        return {
            "decision": "BLOCK",
            "reason": "compound_attack"
        }


    # -----------------------
    # WARN
    # -----------------------

    if score >= 40:

        return {
            "decision": "WARN",
            "reason": "medium_risk"
        }


    if technique_count >= 2:

        return {
            "decision": "WARN",
            "reason": "multiple_techniques"
        }


    # -----------------------
    # ALLOW
    # -----------------------

    return {
        "decision": "ALLOW",
        "reason": "low_risk"
    }
