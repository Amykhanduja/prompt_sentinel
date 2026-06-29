PATTERNS = [
    "new instructions",
    "new task",
    "for the next response",
    "switching tasks",
    "change objectives",
    "ignore current task",
    "different assignment",
    "updated instructions",
    "new objective",
    "starting a new task"
]


def detect_context_switch(prompt: str):

    prompt = prompt.lower()

    for pattern in PATTERNS:

        if pattern in prompt:

            return {
                "technique": "PT-010",
                "name": "Context Switch",
                "severity": "medium",
                "confidence": 1.0
            }

    return None
