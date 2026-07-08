from context.source import ScanSource

TECHNIQUE_WEIGHTS = {
    "PT-009": 30,   # Instruction Override
    "PT-012": 30,   # Indirect Prompt Injection
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
    "PT-031": 40,   # Stored Prompt Injection
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

SOURCE_WEIGHTS = {

    ScanSource.USER: 1.0,

    ScanSource.PDF: 1.1,
    ScanSource.PDF_METADATA: 0.5,
    ScanSource.PDF_FORM: 1.0,
    ScanSource.PDF_ANNOTATION: 0.8,

    ScanSource.DOCX: 1.0,
    ScanSource.DOCX_METADATA: 0.5,

    ScanSource.HTML: 1.0,
    ScanSource.HTML_COMMENT: 0.8,
    ScanSource.HTML_SCRIPT: 1.2,
    ScanSource.HTML_STYLE: 0.3,
    ScanSource.HTML_METADATA: 0.5,

    ScanSource.EMAIL: 1.0,
    ScanSource.EMAIL_SUBJECT: 1.1,
    ScanSource.EMAIL_HEADER: 0.5,
    ScanSource.EMAIL_HTML: 1.0,
    ScanSource.EMAIL_ATTACHMENT: 1.0,

    ScanSource.API_RESPONSE: 1.0,

    ScanSource.ZIP: 1.0,

    ScanSource.UNKNOWN: 1.0,
}


def calculate_risk(detections):

    score = 0

    techniques = set()

    evidence_groups = {}

    risk_breakdown = []

    severity_summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    confidence_sum = 0.0

    for detection in detections:

        technique = detection["technique"]

        pattern = detection.get(
            "pattern",
            technique
        )

        if pattern not in evidence_groups:

            evidence_groups[pattern] = []

        evidence_groups[pattern].append(
            technique
        )

        if technique in techniques:
            continue

        techniques.add(technique)

        base_score = TECHNIQUE_WEIGHTS.get(
            technique,
            0
        )

        confidence = detection.get(
            "confidence",
            1.0
        )

        confidence_sum += confidence

        source = detection.get(
            "source",
            ScanSource.UNKNOWN
        )

        source_multiplier = SOURCE_WEIGHTS.get(
            source,
            1.0
        )

        final_score = int(
            base_score *
            confidence *
            source_multiplier
        )

        score += final_score

        risk_breakdown.append(
            {
                "technique": technique,
                "base_score": base_score,
                "confidence": confidence,
                "source": source,
                "source_multiplier": source_multiplier,
                "final_score": final_score
            }
        )

        severity = detection["severity"]

        if severity in severity_summary:

            severity_summary[severity] += 1


    # -----------------------
    # Compound rules
    # -----------------------

    for rule in COMPOUND_RULES:

        if all(
            item in techniques
            for item in rule["requires"]
        ):

            score += rule["bonus"]

            risk_breakdown.append(
                {
                    "compound": rule["requires"],
                    "bonus": rule["bonus"]
                }
            )


    # -----------------------
    # Duplicate penalty
    # -----------------------

    duplicate_penalty = 0

    for matches in evidence_groups.values():

        if len(matches) > 1:

            duplicate_penalty += (
                len(matches) - 1
            ) * 5
    duplicate_penalty = min(duplicate_penalty,15)

    score -= duplicate_penalty

    score = max(score, 0)

    if duplicate_penalty:
        risk_breakdown.append(
            {
                "duplicate_penalty": duplicate_penalty
            }
        )


    average_confidence = (
        confidence_sum / len(techniques)
        if techniques
        else 0
    )


    if score >= 100:

        overall = "critical"

    elif score >= 60:

        overall = "high"

    elif score >= 30:

        overall = "medium"

    else:

        overall = "low"


    return {

        "score": score,

        "severity": overall,

        "summary": severity_summary,

        "technique_count": len(
            techniques
        ),

        "evidence_groups": len(
            evidence_groups
        ),

        "average_confidence": round(
            average_confidence,
            2
        ),

        "breakdown": risk_breakdown

    }
