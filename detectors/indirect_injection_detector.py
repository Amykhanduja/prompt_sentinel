from utils.pattern_matcher import match_patterns


PATTERNS = [

    "ignore previous instructions",
    "ignore all previous instructions",
    "forget previous instructions",
    "forget all previous instructions",

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
        name="Indirect Prompt Injection",
        severity="high"
    )
