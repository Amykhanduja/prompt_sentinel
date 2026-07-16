from typing import Dict
import logging, json
from datetime import datetime, UTC

logger = logging.getLogger("promptsentinel")
POLICY = {

    "allow": {
        "max_score": 29
    },

    "warn": {
        "max_score": 59
    },

    "review": {
        "max_score": 99
    },

    "block": {
        "max_score": float("inf")
    }

}


def evaluate_policy(risk: Dict) -> Dict:
    """
    Decide the action based on the calculated risk.
    """

    score = risk["score"]

    severity = risk["severity"]

    techniques = risk["technique_count"]

    confidence = risk["average_confidence"]

    critical = risk["summary"]["critical"]

    high = risk["summary"]["high"]

    # -----------------------------------------
    # Hard overrides
    # -----------------------------------------

    if critical >= 2:

        action = "block"

        reason = (
            "Multiple critical techniques detected."
        )

    elif severity == "critical":

        action = "block"

        reason = (
            "Critical prompt injection detected."
        )

    elif high >= 3:

        action = "review"

        reason = (
            "Multiple high-risk techniques detected."
        )

    # -----------------------------------------
    # Score-based policy
    # -----------------------------------------

    else:

        if score <= POLICY["allow"]["max_score"]:

            action = "allow"

            reason = "Low risk."

        elif score <= POLICY["warn"]["max_score"]:

            action = "warn"

            reason = "Moderate risk."

        elif score <= POLICY["review"]["max_score"]:

            action = "review"

            reason = "High risk."

        else:

            action = "block"

            reason = "Critical risk."

    result = {

        "action": action,

        "reason": reason,

        "score": score,

        "severity": severity,

        "confidence": confidence,

        "technique_count": techniques

    }

    logger.info(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "policy_completed",
        "action": result["action"],
        "reason": result["reason"]
    }))

    return result
