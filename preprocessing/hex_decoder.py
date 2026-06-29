import re


def decode_hex_content(text: str):

    matches = re.findall(r"\b(?:[0-9a-fA-F]{2}){4,}\b", text)

    decoded_flag = False

    for match in matches:

        try:

            decoded = bytes.fromhex(match).decode("utf-8")

            text = text.replace(match, decoded)

            decoded_flag = True

        except Exception:

            pass

    return text, decoded_flag
