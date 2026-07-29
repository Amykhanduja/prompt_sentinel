from utils.pattern_matcher import match_patterns


PATTERNS = [

    "hidden instructions",
    "hidden prompt",

    "internal prompt",
    "internal instructions",

    "secret instructions",
    "secret prompt",

    "reveal your prompt",
    "show your prompt"

]


def detect_indirect_injection(
    prompt: str,
    source: str = "user"
):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-012",
        source=source
    )
