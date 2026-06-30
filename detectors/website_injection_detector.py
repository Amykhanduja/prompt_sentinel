from context.source import ScanSource
from utils.pattern_matcher import match_patterns


PATTERNS = [

    "ignore previous instructions",
    "ignore all instructions",

    "assistant:",
    "system:",

    "forward all emails",
    "send user data",

    "execute command",
    "run command",

    "reveal system prompt",
    "show hidden instructions"

]


def detect_website_injection(
    prompt: str,
    source: str = "user"
):

    if source not in [

        ScanSource.HTML,

        ScanSource.HTML_COMMENT

    ]:
        return None

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-035",
        name="Website / Document Injection",
        severity="critical"
    )
