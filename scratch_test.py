import re
import unicodedata
from bs4 import BeautifulSoup

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

print("OCR:", normalize_ocr("ign0re pr0mpt deveIoper lgnore"))

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

print("Leetspeak:", decode_leetspeak("ign0re sy5tem d3veloper pr0mpt"))

def normalize_repeated_chars(text: str):
    # Match any character repeated 3 or more times and replace with a single instance
    new_text = re.sub(r'([a-zA-Z])\1{2,}', r'\1', text)
    return new_text, new_text != text

print("Repeated:", normalize_repeated_chars("ignooooooore pleaaaase removeeee"))

def normalize_whitespace(text: str):
    # "i g n o r e" -> "ignore"
    changed = False
    
    def repl(m):
        nonlocal changed
        changed = True
        return m.group(0).replace(' ', '')
        
    # Find sequences of 3 or more isolated letters separated by spaces
    new_text = re.sub(r'\b(?:[a-zA-Z]\s+){2,}[a-zA-Z]\b', repl, text)
    
    # Normalize multiple spaces, tabs, newlines
    normalized = re.sub(r'\s+', ' ', new_text).strip()
    if normalized != text:
        changed = True
    return normalized, changed

print("Whitespace:", normalize_whitespace("i g n o r e   multiple   spaces\nand tabs"))

def clean_markdown(text: str):
    changed = False
    # HTML
    soup = BeautifulSoup(text, 'html.parser')
    clean = soup.get_text()
    if clean != text:
        changed = True
    
    # Markdown
    old = clean
    clean = re.sub(r'\*\*(.*?)\*\*', r'\1', clean)
    clean = re.sub(r'\*(.*?)\*', r'\1', clean)
    clean = re.sub(r'__(.*?)__', r'\1', clean)
    clean = re.sub(r'_(.*?)_', r'\1', clean)
    clean = re.sub(r'`(.*?)`', r'\1', clean)
    clean = re.sub(r'^>\s*(.*)', r'\1', clean, flags=re.MULTILINE)
    clean = re.sub(r'^#{1,6}\s*(.*)', r'\1', clean, flags=re.MULTILINE)
    
    if clean != old:
        changed = True
        
    return clean, changed

print("Markdown:", clean_markdown("**ignore** `ignore`\n> ignore\n### ignore"))

def normalize_unicode_confusables(text: str):
    # Cyrillic and Greek to Latin
    confusables = {
        'а': 'a', 'В': 'B', 'с': 'c', 'ԁ': 'd', 'е': 'e', 'һ': 'h', 'і': 'i', 'ј': 'j', 'о': 'o', 'р': 'p', 'ԛ': 'q', 'ѕ': 's', 'ԝ': 'w', 'х': 'x', 'у': 'y',
        'А': 'A', 'С': 'C', 'Е': 'E', 'Н': 'H', 'І': 'I', 'Ј': 'J', 'О': 'O', 'Р': 'P', 'Ѕ': 'S', 'Х': 'X', 'У': 'Y',
        'Α': 'A', 'Β': 'B', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Ι': 'I', 'Κ': 'K', 'Μ': 'M', 'Ν': 'N', 'Ο': 'O', 'Ρ': 'P', 'Τ': 'T', 'Υ': 'Y', 'Χ': 'X',
        'ο': 'o', 'ν': 'v'
    }
    changed = False
    new_chars = []
    for char in text:
        if char in confusables:
            new_chars.append(confusables[char])
            changed = True
        else:
            new_chars.append(char)
    return ''.join(new_chars), changed

print("Confusable:", normalize_unicode_confusables("іgnоrе"))

def normalize_homoglyphs(text: str):
    changed = False
    norm = unicodedata.normalize('NFKC', text)
    if norm != text:
        changed = True
    return norm, changed

print("Homoglyphs:", normalize_homoglyphs("＠ $ ｅ"))

def normalize_mixed_language(text: str):
    changed = False
    # Handle "Ignore предыдущие instructions"
    # Translations for common prompt injection words
    translations = {
        'предыдущие': 'previous',
        'предыдущий': 'previous',
        '前の': 'previous',
        'инструкции': 'instructions',
        '指示': 'instructions',
        'игнорируй': 'ignore',
        'игнорировать': 'ignore',
        '無視': 'ignore'
    }
    words = re.findall(r'\b\w+\b', text)
    for w in words:
        if w.lower() in translations:
            text = text.replace(w, translations[w.lower()])
            changed = True
    return text, changed

print("Mixed-lang:", normalize_mixed_language("Ignore предыдущие instructions, Ignore 前の instructions"))
