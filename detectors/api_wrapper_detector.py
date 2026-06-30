from utils.json_extractor import extract_strings_from_json
from utils.pattern_matcher import match_patterns


PATTERNS = [

    "[inst]",
    "[/inst]",
    "<<sys>>",
    "<</sys>>",
    "<|system|>",
    "<|assistant|>",
    "<|user|>",

    "ignore previous instructions",
    "ignore all rules",
    "execute os.popen",
    "system prompt"
]


def detect_api_wrapper(prompt: str, source: str = "user"):

    strings = extract_strings_from_json(prompt)

    if not strings:
        return None

    for value in strings:

        result = match_patterns(
            prompt=value,
            patterns=PATTERNS,
            technique="PT-029",
            name="API Wrapper Injection",
            severity="high"
        )

        if result:
            return result

    return None
