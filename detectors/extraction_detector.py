PATTERNS = [
    "system prompt",
    "developer message",
    "hidden instructions",
    "reveal your prompt"
]


def detect_extraction(prompt):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-013",
                "name": "System Prompt Extraction",
                "severity": "high",
                "confidence": 1.0
            }

    return None
