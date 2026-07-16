from context.source import ScanSource
import logging, json
from datetime import datetime, UTC

logger = logging.getLogger("promptsentinel")
TECHNIQUE_WEIGHTS = {

    "PT-009": 30,
    "PT-012": 30,
    "PT-013": 40,
    "PT-015": 20,
    "PT-018": 35,
    "PT-021": 20,
    "PT-023": 15,
    "PT-024": 15,
    "PT-025": 25,
    "PT-026": 30,
    "PT-027": 35,
    "PT-028": 45,
    "PT-029": 35,
    "PT-031": 40,
    "PT-033": 20,
    "PT-037": 50,
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

    ScanSource.PDF: 1.10,
    ScanSource.PDF_METADATA: 0.50,
    ScanSource.PDF_FORM: 1.00,
    ScanSource.PDF_ANNOTATION: 0.80,

    ScanSource.DOCX: 1.00,
    ScanSource.DOCX_METADATA: 0.50,

    ScanSource.HTML: 1.00,
    ScanSource.HTML_COMMENT: 0.80,
    ScanSource.HTML_SCRIPT: 1.20,
    ScanSource.HTML_STYLE: 0.30,
    ScanSource.HTML_METADATA: 0.50,

    ScanSource.EMAIL: 1.00,
    ScanSource.EMAIL_SUBJECT: 1.10,
    ScanSource.EMAIL_HEADER: 0.50,
    ScanSource.EMAIL_HTML: 1.00,
    ScanSource.EMAIL_ATTACHMENT: 1.00,

    ScanSource.API_RESPONSE: 1.00,

    ScanSource.ZIP: 1.00,

    ScanSource.UNKNOWN: 1.00,
}


FUSION_BONUS = 1.15


def calculate_risk(detections):

    score = 0

    techniques = set()

    confidence_sum = 0.0

    evidence_groups = {}

    breakdown = []

    severity_summary = {

        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for detection in detections:

        technique = detection["technique"]

        if technique in techniques:
            continue

        techniques.add(
            technique
        )

        pattern = detection.get(
            "pattern",
            technique
        )

        evidence_groups.setdefault(
            pattern,
            []
        ).append(
            technique
        )

        base_score = TECHNIQUE_WEIGHTS.get(
            technique,
            0
        )

        confidence = detection.get(
            "confidence",
            1.0
        )

        confidence_sum += confidence

        sources = detection.get(
            "sources"
        )

        if not sources:

            sources = [
                detection.get(
                    "source",
                    ScanSource.UNKNOWN
                )
            ]

        source_multiplier = max(

            SOURCE_WEIGHTS.get(
                source,
                1.0
            )

            for source in sources
        )

        detectors = detection.get(
            "detectors",
            []
        )

        fusion_multiplier = (
            FUSION_BONUS
            if len(detectors) > 1
            else 1.0
        )

        final_score = int(

            base_score
            * confidence
            * source_multiplier
            * fusion_multiplier

        )

        score += final_score

        severity = detection["severity"]

        if severity in severity_summary:

            severity_summary[severity] += 1

        breakdown.append({

            "technique": technique,

            "base_score": base_score,

            "confidence": round(
                confidence,
                3
            ),

            "sources": sources,

            "detectors": detectors,

            "source_multiplier": source_multiplier,

            "fusion_multiplier": fusion_multiplier,

            "final_score": final_score

        })

    for rule in COMPOUND_RULES:

        if all(

            technique in techniques

            for technique in rule["requires"]

        ):

            score += rule["bonus"]

            breakdown.append({

                "compound": rule["requires"],

                "bonus": rule["bonus"]

            })

    duplicate_penalty = 0

    for matches in evidence_groups.values():

        if len(matches) > 1:

            duplicate_penalty += (

                len(matches) - 1

            ) * 5

    duplicate_penalty = min(
        duplicate_penalty,
        15
    )

    score -= duplicate_penalty

    score = max(
        score,
        0
    )

    if duplicate_penalty:

        breakdown.append({

            "duplicate_penalty": duplicate_penalty

        })

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

    result = {

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
            3
        ),

        "breakdown": breakdown

    }

    logger.info(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "risk_completed",
        "score": result["score"],
        "severity": result["severity"]
    }))

    return result
