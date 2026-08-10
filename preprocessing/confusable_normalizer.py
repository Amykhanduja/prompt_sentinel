import re
import unicodedata

def get_script(char: str) -> str:
    try:
        return unicodedata.name(char).split(' ')[0]
    except ValueError:
        return "UNKNOWN"

def is_mixed_script(word: str) -> bool:
    scripts = set()
    for char in word:
        if char.isalpha():
            script = get_script(char)
            if script != "UNKNOWN":
                scripts.add(script)
    return len(scripts) > 1

def is_pure_latin(word: str) -> bool:
    for char in word:
        if char.isalpha() and get_script(char) != "LATIN":
            return False
    return True

def normalize_unicode_confusables(text: str):
    confusables = {
        'а': 'a', 'В': 'B', 'с': 'c', 'ԁ': 'd', 'е': 'e', 'һ': 'h', 'і': 'i', 'ј': 'j', 'о': 'o', 'р': 'p', 'ԛ': 'q', 'ѕ': 's', 'ԝ': 'w', 'х': 'x', 'у': 'y',
        'А': 'A', 'С': 'C', 'Е': 'E', 'Н': 'H', 'І': 'I', 'Ј': 'J', 'О': 'O', 'Р': 'P', 'Ѕ': 'S', 'Х': 'X', 'У': 'Y',
        'Α': 'A', 'Β': 'B', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Ι': 'I', 'Κ': 'K', 'Μ': 'M', 'Ν': 'N', 'Ο': 'O', 'Ρ': 'P', 'Τ': 'T', 'Υ': 'Y', 'Χ': 'X',
        'ο': 'o', 'ν': 'v'
    }
    changed = False
    
    def repl(match):
        nonlocal changed
        word = match.group(0)
        
        # Candidate replacement
        candidate = ""
        word_changed = False
        for char in word:
            if char in confusables:
                candidate += confusables[char]
                word_changed = True
            else:
                candidate += char
                
        if not word_changed:
            return word
            
        # Apply if:
        # 1. Original was mixed script (e.g. Ignоre)
        # 2. Or, candidate becomes purely Latin (e.g. соре -> cope)
        if is_mixed_script(word) or is_pure_latin(candidate):
            changed = True
            return candidate
            
        # Otherwise, preserve original (e.g. Москва)
        return word

    new_text = re.sub(r'\w+', repl, text)
    return new_text, changed
