import re

def normalize_mixed_language(text: str):
    changed = False
    translations = {
        'предыдущие': 'previous',
        'предыдущий': 'previous',
        '前の': 'previous',
        'инструкции': 'instructions',
        '指示': 'instructions',
        'игнорируй': 'ignore',
        'игнорировать': 'ignore',
        '無視': 'ignore'
    }
    words = re.findall(r'\b\w+\b', text)
    for w in words:
        if w.lower() in translations:
            text = text.replace(w, translations[w.lower()])
            changed = True
    return text, changed
