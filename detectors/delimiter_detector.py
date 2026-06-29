from utils.pattern_matcher import match_patterns


PATTERNS = [
    "```system",
    "```assistant",
    "```user",
    "<system>",
    "</system>",
    "<assistant>",
    "</assistant>",
    "[system]",
    "[assistant]"
]

def detect_delimiter(prompt: str):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-027",
        name="Delimiter Injection",
        severity="medium"
    )
