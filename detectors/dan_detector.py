PATTERNS = [
    "you are dan",
    "developer mode",
    "unrestricted ai",
    "act as dan"
]


def detect_dan(prompt):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-018",
                "name": "DAN Jailbreak",
                "severity": "high",
                "confidence": 1.0
            }

    return None
