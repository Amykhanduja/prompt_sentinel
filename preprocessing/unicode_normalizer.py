import unicodedata

def normalize_unicode(text: str):
    # NFKC normalizes fullwidth, math alphanumeric, etc.
    normalized = unicodedata.normalize("NFKC", text)

    changed = normalized != text

    return normalized, changed
