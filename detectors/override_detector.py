from utils.pattern_matcher import match_patterns

PATTERNS = [

    "ignore previous instructions",
    "ignore all previous instructions",

    "forget previous instructions",
    "forget all previous instructions",

    "disregard previous instructions",
    "disregard all previous instructions",

    "override previous instructions",
    "override all previous instructions",
]

def detect_override(prompt: str , source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-009",
        name="Instruction Override",
        severity="high"
    )
