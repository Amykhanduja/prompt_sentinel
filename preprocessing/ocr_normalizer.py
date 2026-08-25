import re

TARGET_WORDS = {
    'ignore', 'prompt', 'developer', 'system', 'instruction', 'instructions',
    'context', 'malicious', 'bypass', 'admin', 'password', 'secret', 'rules',
    'remove', 'history', 'memory', 'forget', 'erase', 'execute', 'print',
    'reveal', 'leak', 'commands', 'override', 'disregard', 'show', 'all', 'with'
}

def normalize_ocr(text: str):
    changed = False
    
    # 1. Line-break artifacts (hyphenated word over a newline)
    new_text = re.sub(r'([a-zA-Z]+)-\n([a-zA-Z]+)', r'\1\2', text)
    if new_text != text:
        changed = True
        text = new_text

    # 2. Isolated OCR separator characters
    new_text = re.sub(r'(?<=[a-zA-Z])\s+[|_]\s+(?=[a-zA-Z])', ' ', text)
    if new_text != text:
        changed = True
        text = new_text

    def repl(match):
        nonlocal changed
        word = match.group(0)
        w = word.lower()
        
        # OCR specific multi-char replacements
        w = w.replace('rn', 'm').replace('vv', 'w')
        
        # Character substitutions
        w = w.replace('0', 'o').replace('5', 's').replace('8', 'b')
        
        # Ambiguous 1, I, l
        variants = {w}
        def expand_variants(current_variants, char_to_replace, possible_replacements):
            new_vars = set()
            for v in current_variants:
                if char_to_replace in v:
                    for r in possible_replacements:
                        new_vars.add(v.replace(char_to_replace, r))
                else:
                    new_vars.add(v)
            return new_vars

        variants = expand_variants(variants, '1', ['i', 'l'])
        variants = expand_variants(variants, 'i', ['i', 'l'])
        variants = expand_variants(variants, 'l', ['i', 'l'])
        
        for v in variants:
            if v in TARGET_WORDS and v != word.lower():
                changed = True
                return v

        return word

    new_text = re.sub(r'[a-zA-Z0-9]+', repl, text)
    if new_text != text:
        changed = True
        text = new_text

    return text, changed
