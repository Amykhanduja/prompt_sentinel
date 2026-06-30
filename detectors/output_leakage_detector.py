from utils.pattern_matcher import match_patterns


PATTERNS = [

    "get_admin_password",
    "get_password",
    "get_secret",
    "get_token",
    "get_key",

    "print the contents of",
    "send me the result",
    "return the result",

    "/etc/passwd",
    "/etc/shadow",

    "select * from users",
    "select * from credentials",
    "select * from passwords",
    "select * from secrets",

    {
        "type": "regex",
        "value": r"(print|send|return|show|display).*(password|secret|token|key)"
    },

    {
        "type": "regex",
        "value": r"select\s+\*\s+from\s+(users|credentials|passwords|secrets)"
    }

]


def detect_output_leakage(prompt: str, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-028",
        name="Output Leakage Request",
        severity="high"
    )
