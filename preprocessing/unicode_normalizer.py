import unicodedata


def normalize_unicode(text: str):
    normalized = unicodedata.normalize("NFC", text)

    changed = normalized != text

    return normalized, changed
