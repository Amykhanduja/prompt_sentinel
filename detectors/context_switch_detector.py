from utils.pattern_matcher import match_patterns

PATTERNS = [
    "new instructions",
    "new task",
    "for the next response",
    "switching tasks",
    "change objectives",
    "ignore current task",
    "different assignment",
    "updated instructions",
    "new objective",
    "starting a new task"
]


def detect_context_switch(prompt: str):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-026",
        name="Context switch",
        severity="medium"
    )
