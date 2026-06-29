PATTERNS = [
    "step 1",
    "step 2",
    "step 3",
    "first",
    "then",
    "finally",
    "after that",
    "next",
    "once completed",
    "continue with"
]


def detect_chained(prompt: str):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-014",
                "name": "Chained Injection",
                "severity": "medium",
                "confidence": 1.0
            }

    return None
