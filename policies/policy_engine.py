def decide_action(risk):

    score = risk["score"]

    severity = risk["severity"]

    summary = risk["summary"]


    # Immediate block conditions

    if summary["critical"] >= 1:
        return "BLOCK"


    if score >= 100:
        return "BLOCK"


    # High confidence warning

    if severity == "high":

        if summary["high"] >= 2:
            return "BLOCK"

        return "WARN"


    # Medium findings

    if severity == "medium":

        if summary["medium"] >= 3:
            return "WARN"

        return "ALLOW"


    return "ALLOW"
