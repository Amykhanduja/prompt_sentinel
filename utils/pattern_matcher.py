import re


def match_patterns(
    prompt: str,
    patterns: list,
    technique: str,
    name: str,
    severity: str
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
                        "name": name,
                        "severity": severity,
                        "matched": True,
                        "pattern": value
                    }

            else:

                if value.lower() in text:
                    return {
                        "technique": technique,
                        "name": name,
                        "severity": severity,
                        "matched": True,
                        "pattern": value
                    }


        else:

            if pattern.lower() in text:
                return {
                    "technique": technique,
                    "name": name,
                    "severity": severity,
                    "matched": True,
                    "pattern": pattern
                }


    return None
