from utils.pattern_matcher import match_patterns


PATTERNS = [

    "{{system}}",
    "{{user}}",
    "{{assistant}}",

    "<system>",
    "</system>",
    "<user>",
    "</user>",
    "<assistant>",
    "</assistant>",

    "system:",
    "user:",
    "assistant:",

    "```assistant",
    "```system",
    "```user",

    "# system",
    "# user",
    "# assistant",

    "ignore previous instructions",
    "new instructions",
    "override instructions"

]

def detect_template(prompt: str, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-015",
        name="Template Injection",
        severity="medium"
    )
