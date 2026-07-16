import unicodedata

def normalize_homoglyphs(text: str):
    normalized = unicodedata.normalize('NFKC', text)
    changed = normalized != text
    return normalized, changed
