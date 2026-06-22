import re
import base64


def decode_base64_content(text: str) -> str:

    matches = re.findall(
        r"[A-Za-z0-9+/]{8,}={0,2}",
        text
    )

    decoded_chunks = []

    for item in matches:
        try:
            decoded = base64.b64decode(item).decode(
                "utf-8",
                errors="ignore"
            )

            decoded_chunks.append(decoded)

        except Exception:
            pass

    if decoded_chunks:
        return text + "\n" + "\n".join(decoded_chunks)

    return text
