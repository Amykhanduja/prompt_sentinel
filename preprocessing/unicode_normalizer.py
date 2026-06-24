import unicodedata


def normalize_unicode(text: str):

    normalized = unicodedata.normalize("NFKC", text)

    changed = normalized != text

    return normalized, changed
