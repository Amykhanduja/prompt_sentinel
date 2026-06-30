from utils.pattern_matcher import match_patterns


PATTERNS = [

    "i am your developer",
    "i'm your developer",
    "you are talking to your developer",

    "admin mode",
    "administrator mode",
    "system: admin mode activated",
    "developer mode",

    "system:",
    "assistant:",
    "developer:",

    {
        "type": "regex",
        "value": r"as a (?:certified|trusted|authorized|official)?\s*(?:admin|administrator|developer|security engineer|red teamer|red team|employee|maintainer|owner)"
    }

]


def detect_privileged_identity(prompt: str, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-027",
        name="Privileged Identity Injection",
        severity="medium"
    )
