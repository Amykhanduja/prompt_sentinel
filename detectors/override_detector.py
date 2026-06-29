from utils.pattern_matcher import match_patterns

PATTERNS = [
    "ignore previous instructions",
    "forget all instructions",
    "disregard all instructions",
    "ignore all prior directives"
]

def detect_override(prompt):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-009",
        name="Instruction Override",
        severity="high"
    )
