from utils.pattern_matcher import match_patterns
from context.source import ScanSource

PATTERNS = [

    "ignore previous instructions",
    "ignore all instructions",
    "disregard previous instructions",

    "assistant: ignore",
    "assistant: execute",

    "send user data",
    "send the results",
    "forward all data",
    "forward all emails",

    "reveal system prompt",
    "show hidden instructions",

    "execute command",
    "run command",

    "call this tool",
    "use this function"

]


def detect_api_response_injection(prompt: str, source: str = "user"):

    if source != ScanSource.API_RESPONSE:
        return None

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-036",
        name="API Response Poisoning",
        severity="critical"
    )
