import re

def normalize_repeated_chars(text: str):
    changed = False
    
    # 1. Letters repeated 3+ times collapsed to 1 (e.g. Igggnore -> Ignore)
    # Does not affect 2 repetitions (e.g. committee, successful)
    new_text = re.sub(r'([a-zA-Z])\1{2,}', r'\1', text)
    if new_text != text:
        changed = True
        text = new_text
        
    # 2. Punctuation repeated 3+ times collapsed to 1 (e.g. !!! -> !)
    new_text = re.sub(r'([!?.,;\-])\1{2,}', r'\1', text)
    if new_text != text:
        changed = True
        text = new_text

    return text, changed
