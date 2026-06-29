PATTERNS = [
    "</system>",
    "<system>",
    "<assistant>",
    "</assistant>",
    "### system prompt",
    "begin instructions",
    "end instructions",
    "system:",
    "assistant:",
]


def detect_delimiter(prompt: str):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-011",
                "name": "Delimiter Escape",
                "severity": "high",
                "confidence": 1.0
            }

    return None
