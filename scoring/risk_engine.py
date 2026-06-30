TECHNIQUE_WEIGHTS = {
    "PT-009": 30,   # Instruction Override
    "PT-013": 40,   # System Prompt Extraction
    "PT-015": 20,   #
    "PT-018": 35,   # Roleplay Injection
    "PT-021": 20,
    "PT-023": 15,
    "PT-024": 15,
    "PT-025": 25,
    "PT-026": 30,
    "PT-027": 35,   # Privileged Identity
    "PT-028": 45,   # Output Leakage
    "PT-029": 35,   # API Wrapper
    "PT-033": 20,   # Thought Simulation
    "PT-037": 50,   # Format Token Injection
}

COMPOUND_RULES = [

    {
        "requires": [
            "PT-009",
            "PT-028"
        ],
        "bonus": 30
    },

    {
        "requires": [
            "PT-009",
            "PT-029"
        ],
        "bonus": 25
    },

    {
        "requires": [
            "PT-027",
            "PT-009"
        ],
        "bonus": 20
    }

]

def calculate_risk(detections):

    score = 0


    techniques = {
        d["technique"]
        for d in detections
    }


    # normal scoring
    for technique in techniques:

        score += TECHNIQUE_WEIGHTS.get(
            technique,
            0
        )


    # compound escalation
    for rule in COMPOUND_RULES:

        if all(
            item in techniques
            for item in rule["requires"]
        ):

            score += rule["bonus"]


    if score >= 100:

        severity = "critical"

    elif score >= 60:

        severity = "high"

    elif score >= 30:

        severity = "medium"

    else:

        severity = "low"


    return {
        "score": score,
        "severity": severity
    }
