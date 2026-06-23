def decide_action(risk):

    score = risk["score"]

    if score >= 80:
        return "BLOCK"

    elif score >= 40:
        return "MONITOR"

    else:
        return "ALLOW"
