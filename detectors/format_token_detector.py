from utils.pattern_matcher import match_patterns


PATTERNS = [

    # ChatML
    "<|im_start|>",
    "<|im_end|>",
    "<|system|>",
    "<|assistant|>",
    "<|user|>",

    # Llama / Mixtral
    "[inst]",
    "[/inst]",
    "<<sys>>",
    "<</sys>>",

    # BOS / EOS
    "<s>",
    "</s>",

    # Common role tokens
    "### system",
    "### assistant",
    "### user"
]


def detect_format_token(prompt: str, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-037",
        name="Format Token Injection",
        severity="critical"
    )
