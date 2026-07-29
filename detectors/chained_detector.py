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

    "after completing this",
    "once completed",
    "after you finish"

]

def detect_chained(prompt: str, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-027",
        source=source
    )
