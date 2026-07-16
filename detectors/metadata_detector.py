from utils.pattern_matcher import match_patterns
from context.source import ScanSource

PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "assistant:",
    "system:",
    "forward all emails",
    "send the results",
    "send user data",
    "execute command",
    "run command",
    "reveal system prompt",
    "show hidden instructions"
]


def detect_metadata_injection(
    prompt: str,
    source: str = "user"
):

    if source not in [
        ScanSource.PDF_METADATA,
        ScanSource.DOCX_METADATA
    ]:
        return None

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-034",
        source=source
    )
