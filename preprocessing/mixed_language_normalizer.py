import unicodedata
import re

def get_script(char: str) -> str:
    try:
        name = unicodedata.name(char)
        # e.g., "LATIN SMALL LETTER A" -> "LATIN"
        return name.split(' ')[0]
    except ValueError:
        return "UNKNOWN"

def normalize_mixed_language(text: str):
    changed = False
    detected = False
    
    # Identify mixed scripts inside individual tokens
    tokens = re.findall(r'\w+', text)
    
    for token in tokens:
        scripts = set()
        for char in token:
            if char.isalpha(): 
                script = get_script(char)
                if script not in ("UNKNOWN"):
                    scripts.add(script)
        
        if len(scripts) > 1:
            detected = True
            break
            
    # As per instructions: do NOT translate.
    # Return the text unchanged, but emit the detection flag.
    # To maintain backward compatibility with pipeline.py unpack, we return (text, detected).
    return text, detected
