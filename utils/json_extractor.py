import json


def extract_json_strings(data):

    strings = []

    if isinstance(data, dict):

        for value in data.values():
            strings.extend(
                extract_json_strings(value)
            )

    elif isinstance(data, list):

        for item in data:
            strings.extend(
                extract_json_strings(item)
            )

    elif isinstance(data, str):

        strings.append(data)

    return strings


def extract_strings_from_json(text: str):

    try:

        data = json.loads(text)

        return extract_json_strings(data)

    except Exception:

        return []
