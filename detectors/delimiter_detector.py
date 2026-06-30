from utils.pattern_matcher import match_patterns

PATTERNS = [
    "### system prompt ###",
    "system prompt",

    "begin instructions",
    "end instructions",

    "begin system prompt",
    "end system prompt",

    "<system>",
    "</system>",
    "<assistant>",
    "</assistant>",

    "--- system ---",
    "--- assistant ---"
]
def detect_delimiter(prompt: str, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-027",
        name="Delimiter Injection",
        severity="medium"
    )
