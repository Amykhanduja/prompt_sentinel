from preprocessing.unicode_normalizer import normalize_unicode
from preprocessing.base64_decoder import decode_base64_content
from preprocessing.hex_decoder import decode_hex_content
from preprocessing.url_decoder import decode_url_content
from preprocessing.html_entity_decoder import decode_html_entities
from preprocessing.zero_width_remover import remove_zero_width


def decode_once(prompt: str):

    changed = False

    prompt, base64_flag = decode_base64_content(prompt)
    changed |= base64_flag

    prompt, hex_flag = decode_hex_content(prompt)
    changed |= hex_flag

    prompt, url_flag = decode_url_content(prompt)
    changed |= url_flag

    prompt, html_flag = decode_html_entities(prompt)
    changed |= html_flag

    prompt, zero_width_flag = remove_zero_width(prompt)
    changed |= zero_width_flag

    return (
        prompt,
        changed,
        {
            "base64_flag": base64_flag,
            "hex_flag": hex_flag,
            "url_flag": url_flag,
            "html_flag": html_flag,
            "zero_width_flag": zero_width_flag
        }
    )


def iterative_decode(prompt: str, max_iterations: int = 5):

    flags = {
        "base64_flag": False,
        "hex_flag": False,
        "url_flag": False,
        "html_flag": False,
        "zero_width_flag": False
    }

    for _ in range(max_iterations):

        prompt, changed, current_flags = decode_once(prompt)

        for key, value in current_flags.items():
            flags[key] = flags[key] or value

        if not changed:
            break

    return prompt, flags


def preprocess_prompt(prompt: str):

    prompt, unicode_flag = normalize_unicode(prompt)

    prompt, flags = iterative_decode(prompt)

    return {
        "prompt": prompt,
        "unicode_flag": unicode_flag,
        **flags
    }
