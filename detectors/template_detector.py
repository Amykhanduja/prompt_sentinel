PATTERNS = [
    "```system",
    "```assistant",
    "```user",
    "{{system}}",
    "{{prompt}}",
    "{% system %}",
    "# system prompt",
    "## system prompt",
    "### system prompt",
    "system prompt:"
]


def detect_template(prompt: str):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-015",
                "name": "Template / Markdown Injection",
                "severity": "medium",
                "confidence": 1.0
            }

    return None
