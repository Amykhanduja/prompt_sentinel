PATTERNS = [
    "ignore previous instructions in this document",
    "the following instructions are for the ai",
    "embedded instructions",
    "hidden instructions",
    "contained in this webpage",
    "contained in this document",
    "<!--",
    "-->",
    "<script>",
    "</script>"
]


def detect_indirect(prompt: str):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-012",
                "name": "Indirect Prompt Injection",
                "severity": "high",
                "confidence": 1.0
            }

    return None
