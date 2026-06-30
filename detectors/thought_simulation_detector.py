from utils.pattern_matcher import match_patterns


PATTERNS = [

    {
        "type": "regex",
        "value": r"(hypothetically|theoretically|imagine|suppose|what if).*(ignore|bypass|override|system prompt|os\.popen|eval|exec|shell|command)"
    },

    {
        "type": "regex",
        "value": r"(hypothetically|theoretically|imagine|suppose|what if).*(no restrictions|without restrictions|unrestricted)"
    },

    {
        "type": "regex",
        "value": r"if someone (wanted|were) to.*(ignore|bypass|override|os\.popen|eval|exec|shell|command)"
    },

    {
        "type": "regex",
        "value": r"pretend.*(ignore|override|bypass).*(instructions|system prompt)"
    }

]


def detect_thought_simulation(prompt: str, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-033",
        name="Thought Simulation Bypass",
        severity="medium"
    )
