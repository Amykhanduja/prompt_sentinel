import re

TARGET_WORDS = {
    'ignore', 'prompt', 'developer', 'system', 'instruction', 'instructions',
    'context', 'malicious', 'bypass', 'admin', 'password', 'secret', 'rules',
    'remove', 'history', 'memory', 'forget', 'erase', 'execute', 'print',
    'reveal', 'leak', 'commands', 'override', 'disregard'
}

def normalize_ocr(text: str):
    changed = False
    
    def replace_func(match):
        nonlocal changed
        word = match.group(0)
        w = word.lower()
        w = w.replace('0', 'o').replace('5', 's').replace('8', 'b')
        w = w.replace('rn', 'm').replace('vv', 'w')
        
        # Combinations for 1, i, l, I
        variants = {w}
        if '1' in w:
            variants.add(w.replace('1', 'i'))
            variants.add(w.replace('1', 'l'))
        if 'i' in w:
            variants.add(w.replace('i', 'l'))
        if 'l' in w:
            variants.add(w.replace('l', 'i'))
            
        new_variants = set(variants)
        for v in variants:
            if '1' in v:
                new_variants.add(v.replace('1', 'i'))
                new_variants.add(v.replace('1', 'l'))
            if 'i' in v:
                new_variants.add(v.replace('i', 'l'))
            if 'l' in v:
                new_variants.add(v.replace('l', 'i'))
                
        for v in new_variants:
            if v in TARGET_WORDS and v != word.lower():
                changed = True
                if word[0].isupper():
                    return v.capitalize()
                return v
        return word

    new_text = re.sub(r'[a-zA-Z0-9]+', replace_func, text)
    return new_text, changed
