import re

def normalize_repeated_chars(text: str):
    new_text = re.sub(r'([a-zA-Z])\1{2,}', r'\1', text)
    return new_text, new_text != text
