import re

def normalize_whitespace(text: str):
    changed = False
    
    # 1. Normalize line endings to canonical \n
    new_text = text.replace('\r\n', '\n').replace('\r', '\n')
    if new_text != text:
        changed = True
        text = new_text

    # 2. Normalize spaced out words: I g n o r e -> Ignore
    def repl_spaced(m):
        return m.group(0).replace(' ', '')
        
    new_text = re.sub(r'\b(?:[a-zA-Z0-9]\s+){2,}[a-zA-Z0-9]\b', repl_spaced, text)
    if new_text != text:
        changed = True
        text = new_text
        
    # 3. Collapse multiple spaces/tabs into a single space, but PRESERVE newlines
    new_text = re.sub(r'[^\S\n]{2,}', ' ', text)
    if new_text != text:
        changed = True
        text = new_text

    return text.strip(), changed
