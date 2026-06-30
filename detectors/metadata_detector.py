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

    print("SOURCE =", source)

    print(
        source == ScanSource.PDF_METADATA,
        source == ScanSource.DOCX_METADATA
    )

    if source not in [
        ScanSource.PDF_METADATA,
        ScanSource.DOCX_METADATA
    ]:
        print("RETURNING NONE")
        return None

    print("CALLING MATCHER")

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-034",
        name="EXIF Metadata Injection",
        severity="critical"
    )
