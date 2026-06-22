from preprocessing.unicode_normalizer import normalize_unicode
from preprocessing.base64_decoder import decode_base64_content


def preprocess_prompt(prompt: str):

    prompt = normalize_unicode(prompt)

    prompt = decode_base64_content(prompt)

    return prompt
