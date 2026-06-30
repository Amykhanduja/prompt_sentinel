from utils.pattern_matcher import match_patterns

PATTERNS = [
    # Existing DAN patterns
    "you are dan",
    "developer mode",
    "unrestricted ai",
    "act as dan",

    # Generic roleplay patterns
    "you are now",
    "pretend to be",
    "act as",
    "assume the role",
    "simulate",
    "from now on you are",
    "behave like",
    "roleplay as"
]

def detect_dan(prompt, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-018",
        name="Roleplay Injection",
        severity="high"
    )
