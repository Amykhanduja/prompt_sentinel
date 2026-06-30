from preprocessing.base64_decoder import decode_base64_content
from preprocessing.hex_decoder import decode_hex_content
from preprocessing.url_decoder import decode_url_content
from preprocessing.html_entity_decoder import decode_html_entities
from preprocessing.zero_width_remover import remove_zero_width
from preprocessing.unicode_normalizer import normalize_unicode


def decode_once(prompt: str):

    changed = False

    prompt, unicode_flag = normalize_unicode(prompt)
    changed |= unicode_flag

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
            "unicode_flag": unicode_flag,
            "base64_flag": base64_flag,
            "hex_flag": hex_flag,
            "url_flag": url_flag,
            "html_flag": html_flag,
            "zero_width_flag": zero_width_flag
        }
    )


def iterative_decode(prompt: str, max_iterations: int = 5):

    flags = {
        "unicode_flag": False,
        "base64_flag": False,
        "hex_flag": False,
        "url_flag": False,
        "html_flag": False,
        "zero_width_flag": False
    }


    for _ in range(max_iterations):

        prompt, changed, current_flags = decode_once(prompt)


        for key, value in current_flags.items():
            flags[key] |= value


        if not changed:
            break


    return {
        "prompt": prompt,
        "flags": flags
    }


def preprocess_prompt(prompt: str):

    result = iterative_decode(prompt)

    response = {
        "prompt": result["prompt"],

        # new structure
        "flags": result["flags"],

        # backward compatibility
        "unicode_flag": result["flags"]["unicode_flag"],
        "base64_flag": result["flags"]["base64_flag"],
        "hex_flag": result["flags"]["hex_flag"],
        "url_flag": result["flags"]["url_flag"],
        "html_flag": result["flags"]["html_flag"],
        "zero_width_flag": result["flags"]["zero_width_flag"],
    }

    return response
