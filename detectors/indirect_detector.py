from utils.pattern_matcher import match_patterns

PATTERNS = [
    "ignore previous instructions in this document",
    "the following instructions are for the ai",
    "embedded instructions",
    "hidden instructions",
    "contained in this webpage",
    "contained in this document",
    "for ai only",
    "for the language model",
    "for the ai assistant",
    "the following instructions are for the ai",
    "ignore previous instructions",
    "ignore previous system instructions",
    "disregard previous instructions",
    "follow these hidden instructions",
    "do not reveal this to the user",
    "assistant:",
    "system:",
    "<!--",
    "<script>"
]


def detect_indirect(prompt: str):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-012",
        name="Indirect Prompt Injection",
        severity="high"
    )
