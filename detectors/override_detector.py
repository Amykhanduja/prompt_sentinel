PATTERNS = [
    "ignore previous instructions",
    "forget all instructions",
    "disregard all instructions",
    "ignore all prior directives"
]


def detect_override(prompt: str):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-009",
                "name": "Instruction Override",
                "severity": "high",
                "confidence": 1.0
            }

    return None
