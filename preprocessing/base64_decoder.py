import re
import base64


def decode_base64_content(text: str):

    matches = re.findall(
        r"[A-Za-z0-9+/]{8,}={0,2}",
        text
    )

    decoded_chunks = []

    for item in matches:
        try:
            decoded = base64.b64decode(
                item,
                validate=True
            ).decode(
               "utf-8",
               errors="ignore"
            )
            if len(decoded.strip()) < 4:
                continue

            if not any(c.isalpha() for c in decoded):
                continue

            decoded_chunks.append(decoded)

        except Exception:
            pass

    if decoded_chunks:
        return (
           text + "\n" + "\n".join(decoded_chunks),
           True
        )

    return text, False
