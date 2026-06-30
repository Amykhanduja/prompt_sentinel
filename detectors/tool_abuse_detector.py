from utils.pattern_matcher import match_patterns


PATTERNS = [
    "call this tool",
    "use this function",
     "use the browser",
    "use browser tool",
    "use the terminal",
    "execute this command",
    "run this command",
    "call the api",
    "use the api",
    "read the file",
    "write to file",
    "open this url",
    "send the results",
    "download this file",
    "run this code",
    "invoke the tool",
    "access the api",
    "make a tool call"
]


def detect_tool_abuse(prompt: str, source: str = "user"):

    return match_patterns(
        prompt=prompt,
        patterns=PATTERNS,
        technique="PT-029",
        name="Tool Abuse",
        severity="high"
    )
