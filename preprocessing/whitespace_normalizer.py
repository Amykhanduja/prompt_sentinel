import re

def normalize_whitespace(text: str):
    changed = False
    
    def repl(m):
        nonlocal changed
        changed = True
        return m.group(0).replace(' ', '')
        
    new_text = re.sub(r'\b(?:[a-zA-Z]\s+){2,}[a-zA-Z]\b', repl, text)
    
    normalized = re.sub(r'\s+', ' ', new_text).strip()
    if normalized != text:
        changed = True
    return normalized, changed
