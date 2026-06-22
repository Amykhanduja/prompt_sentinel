import unicodedata


def normalize_unicode(text: str) -> str:
    """
    Normalize unicode characters to their ASCII equivalent where possible.
    """

    return unicodedata.normalize("NFKC", text)
