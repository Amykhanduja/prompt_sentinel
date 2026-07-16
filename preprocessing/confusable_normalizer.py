def normalize_unicode_confusables(text: str):
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
