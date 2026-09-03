from utils.pattern_matcher import match_patterns
from context.source import ScanSource

PATTERNS = [
    {"type": "regex", "value": r"\b(ignore|disregard|forget|override|drop)\s+(all\s+)?(previous|prior|earlier|system|initial)\s+(instructions?|rules?|prompts?|guidelines?|database)\b"},
    {"type": "regex", "value": r"\b(note\s+content\s+retrieved|system\s+template\s+header|database\s+record\s+field|document\s+content|retrieved\s+context|metadata\s+block|search\s+result\s+snippet).*?(ignore|override|disregard|execute|drop)\b"},
    {"type": "regex", "value": r"\b(execute|run)\s+(the\s+)?(following\s+)?(command|instruction)\b"},
    
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
        source=source
    )
