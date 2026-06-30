from utils.pattern_matcher import match_patterns
from context.source import ScanSource

PATTERNS = [

    "ignore previous instructions",
    "ignore all instructions",
    "disregard previous instructions",
    "forget previous instructions",

    "assistant:",
    "system:",
    "assistant: execute",
    "assistant: ignore",

    "forward all content",
    "forward all emails",

    "send all data",
    "send user data",
    "send this to",

    "delete all files",

    "execute the following command",
    "execute command",
    "run command",

    "reveal your system prompt",
    "reveal system prompt",

    "show hidden commands",
    "show hidden instructions",
]

def detect_stored_injection(prompt: str,source: str = "user"):

    if source == ScanSource.USER:
        return None

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-031",
        name="Stored Prompt Injection",
        severity="critical"
    )
