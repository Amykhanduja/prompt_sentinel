from preprocessing.unicode_normalizer import normalize_unicode
from preprocessing.base64_decoder import decode_base64_content


def preprocess_prompt(prompt: str):

    prompt, unicode_flag = normalize_unicode(prompt)

    prompt, base64_flag = decode_base64_content(prompt)

    return {
        "prompt": prompt,
        "unicode_flag": unicode_flag,
        "base64_flag": base64_flag
    }
