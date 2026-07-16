import re

TARGET_WORDS = {
    'ignore', 'prompt', 'developer', 'system', 'instruction', 'instructions',
    'context', 'malicious', 'bypass', 'admin', 'password', 'secret', 'rules',
    'remove', 'history', 'memory', 'forget', 'erase', 'execute', 'print',
    'reveal', 'leak', 'commands', 'override', 'disregard'
}

def decode_leetspeak(text: str):
    changed = False
    
    def replace_func(match):
        nonlocal changed
        word = match.group(0)
        w = word.lower()
        w = w.replace('4', 'a').replace('3', 'e').replace('0', 'o').replace('5', 's').replace('7', 't').replace('8', 'b')
        
        variants = {w}
        if '1' in w:
            variants.add(w.replace('1', 'i'))
            variants.add(w.replace('1', 'l'))
            
        for v in variants:
            if v in TARGET_WORDS and v != word.lower():
                changed = True
                if word[0].isupper():
                    return v.capitalize()
                return v
        return word
        
    new_text = re.sub(r'[a-zA-Z0-9]+', replace_func, text)
    return new_text, changed
