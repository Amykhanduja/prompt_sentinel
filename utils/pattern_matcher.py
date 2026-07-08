import re


def match_patterns(
    prompt: str,
    patterns: list,
    technique: str,
    source: str = "user"
):

    text = prompt.lower()

    for pattern in patterns:

        if isinstance(pattern, dict):

            value = pattern["value"]

            pattern_type = pattern.get(
                "type",
                "contains"
            )

            if pattern_type == "regex":

                if re.search(
                    value,
                    text
                ):

                    return {
                        "technique": technique,
                        "confidence": 0.90,
                        "matched": True,
                        "pattern": value,
                        "source": source
                    }

            else:

                if value.lower() in text:

                    return {
                        "technique": technique,
                        "confidence": 0.80,
                        "matched": True,
                        "pattern": value,
                        "source": source
                    }

        else:

            if pattern.lower() in text:

                return {
                    "technique": technique,
                    "confidence": 0.80,
                    "matched": True,
                    "pattern": pattern,
                    "source": source
                }

    return None
