import unicodedata

def normalize_homoglyphs(text: str):
    changed = False
    
    # 1. Unicode NFKC normalization
    new_text = unicodedata.normalize("NFKC", text)
    if new_text != text:
        changed = True
        text = new_text

    # 2. Explicit, finite, reviewable mapping of common prompt-injection homoglyphs
    homoglyphs = {
        # Circled
        'Ⓘ': 'I', 'ⓖ': 'g', 'ⓝ': 'n', 'ⓞ': 'o', 'ⓡ': 'r', 'ⓔ': 'e',
        # Math Sans-serif / Bold / Italic
        '𝐈': 'I', '𝐠': 'g', '𝐧': 'n', '𝐨': 'o', '𝐫': 'r', '𝐞': 'e',
        '𝐼': 'I', '𝑔': 'g', '𝑛': 'n', '𝑜': 'o', '𝑟': 'r', '𝑒': 'e',
        '𝙸': 'I', '𝚐': 'g', '𝚗': 'n', '𝚘': 'o', '𝚛': 'r', '𝚎': 'e',
        '𝟙': '1', '𝟘': '0'
    }
    
    new_chars = []
    for char in text:
        if char in homoglyphs:
            new_chars.append(homoglyphs[char])
            changed = True
        else:
            new_chars.append(char)
            
    return ''.join(new_chars), changed
