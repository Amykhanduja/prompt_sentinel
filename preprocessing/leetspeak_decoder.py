import re

TARGET_WORDS = {
    'ignore', 'prompt', 'developer', 'system', 'instruction', 'instructions',
    'context', 'malicious', 'bypass', 'admin', 'password', 'secret', 'rules',
    'remove', 'history', 'memory', 'forget', 'erase', 'execute', 'print',
    'reveal', 'leak', 'commands', 'override', 'disregard', 'show', 'all'
}

def decode_leetspeak(text: str):
    changed = False
    
    def repl(match):
        nonlocal changed
        word = match.group(0)
        
        if word.isalpha():
            return word
            
        w = word.lower()
        
        # Strong substitutions
        w = w.replace('0', 'o').replace('3', 'e').replace('4', 'a').replace('8', 'b')
        
        # Ambiguous substitutions
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
        variants = expand_variants(variants, '5', ['s'])
        variants = expand_variants(variants, '7', ['t'])
        
        for v in variants:
            if v in TARGET_WORDS and v != word.lower():
                changed = True
                if word[0].isupper():
                    return v.capitalize()
                return v
                
        return word

    new_text = re.sub(r'[a-zA-Z0-9]+', repl, text)
    return new_text, changed
