PATTERNS = [
    # Existing DAN patterns
    "you are dan",
    "developer mode",
    "unrestricted ai",
    "act as dan",

    # Generic roleplay patterns
    "you are now",
    "pretend to be",
    "act as",
    "assume the role",
    "simulate",
    "from now on you are",
    "behave like",
    "roleplay as"
]

def detect_dan(prompt):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-018",
                "name": "Roleplay Injection",
                "severity": "high",
                "confidence": 1.0
            }

    return None
