import re

def normalize_ocr(text: str):
    changed = False
    
    # 1. Line-break artifacts (hyphenated word over a newline)
    # e.g. "exam-\nple" -> "example"
    new_text = re.sub(r'([a-zA-Z]+)-\n([a-zA-Z]+)', r'\1\2', text)
    if new_text != text:
        changed = True
        text = new_text

    # 2. Isolated OCR separator characters that randomly break sentences
    # e.g., "Ignore | previous" -> "Ignore previous"
    # But be conservative to not destroy code formatting.
    # Only remove if it's flanked by letters/spaces in a way that suggests a scanning artifact
    new_text = re.sub(r'(?<=[a-zA-Z])\s+[|_]\s+(?=[a-zA-Z])', ' ', text)
    if new_text != text:
        changed = True
        text = new_text

    return text, changed
