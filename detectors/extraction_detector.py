from utils.pattern_matcher import match_patterns

PATTERNS = [
    "system prompt",
    "developer message",
    "hidden instructions",
    "reveal your prompt"
]


def detect_extraction(prompt, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-013",
        name="System Prompt Extraction",
        severity="high"
    )
