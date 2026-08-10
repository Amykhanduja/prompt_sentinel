import unicodedata

def normalize_homoglyphs(text: str):
    # Explicit, finite, reviewable mapping of common prompt-injection homoglyphs
    homoglyphs = {
        # Fullwidth
        'Ｉ': 'I', 'ｇ': 'g', 'ｎ': 'n', 'ｏ': 'o', 'ｒ': 'r', 'ｅ': 'e',
        'ａ': 'a', 'ｌ': 'l', 'ｐ': 'p', 'ｖ': 'v', 'ｉ': 'i', 'ｕ': 'u', 'ｓ': 's', 'ｔ': 't', 'ｃ': 'c',
        # Circled
        'Ⓘ': 'I', 'ⓖ': 'g', 'ⓝ': 'n', 'ⓞ': 'o', 'ⓡ': 'r', 'ⓔ': 'e',
        # Math Sans-serif / Bold / Italic
        '𝐈': 'I', '𝐠': 'g', '𝐧': 'n', '𝐨': 'o', '𝐫': 'r', '𝐞': 'e',
        '𝐼': 'I', '𝑔': 'g', '𝑛': 'n', '𝑜': 'o', '𝑟': 'r', '𝑒': 'e',
        '𝙸': 'I', '𝚐': 'g', '𝚗': 'n', '𝚘': 'o', '𝚛': 'r', '𝚎': 'e',
        '𝟙': '1', '𝟘': '0'
    }
    changed = False
    new_chars = []
    for char in text:
        if char in homoglyphs:
            new_chars.append(homoglyphs[char])
            changed = True
        else:
            new_chars.append(char)
    return ''.join(new_chars), changed
