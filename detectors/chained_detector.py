from utils.pattern_matcher import match_patterns


PATTERNS = [

    "step 1:",
    "step 2:",
    "step 3:",

    "step one",
    "step two",
    "step three",

    "first do this then",
    "do this first then",

    "first",
    "then",
    "after that",
    "finally",

    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",

    "after completing this",
    "once completed",
    "after you finish"

]

def detect_chained(prompt: str):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-027",
        name="Chained Injection",
        severity="high"
    )
