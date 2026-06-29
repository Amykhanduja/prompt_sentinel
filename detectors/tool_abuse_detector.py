PATTERNS = [
    "use the browser",
    "use browser tool",
    "use the terminal",
    "execute this command",
    "run this command",
    "call the api",
    "use the api",
    "read the file",
    "write to file",
    "open this url",
    "send the results",
    "download this file"
]


def detect_tool_abuse(prompt: str):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-013",
                "name": "Tool Abuse",
                "severity": "high",
                "confidence": 1.0
            }

    return None
