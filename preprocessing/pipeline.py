from preprocessing.unicode_normalizer import normalize_unicode
from preprocessing.base64_decoder import decode_base64_content
from preprocessing.hex_decoder import decode_hex_content
from preprocessing.url_decoder import decode_url_content
from preprocessing.html_entity_decoder import decode_html_entities
from preprocessing.zero_width_remover import remove_zero_width

def preprocess_prompt(prompt: str):

    prompt, unicode_flag = normalize_unicode(prompt)

    prompt, base64_flag = decode_base64_content(prompt)

    prompt, hex_flag = decode_hex_content(prompt)

    prompt, url_flag = decode_url_content(prompt)

    prompt, html_flag = decode_html_entities(prompt)

    prompt, zero_width_flag = remove_zero_width(prompt)

    return {
        "prompt": prompt,
        "unicode_flag": unicode_flag,
        "hex_flag": hex_flag,
        "url_flag": url_flag,
        "base64_flag": base64_flag,
        "html_flag": html_flag,
        "zero_width_flag": zero_width_flag
    }
