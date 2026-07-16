from preprocessing.base64_decoder import decode_base64_content
from preprocessing.hex_decoder import decode_hex_content
from preprocessing.url_decoder import decode_url_content
from preprocessing.html_entity_decoder import decode_html_entities
from preprocessing.zero_width_remover import remove_zero_width
from preprocessing.unicode_normalizer import normalize_unicode

# New imports
from preprocessing.ocr_normalizer import normalize_ocr
from preprocessing.leetspeak_decoder import decode_leetspeak
from preprocessing.repeated_char_normalizer import normalize_repeated_chars
from preprocessing.whitespace_normalizer import normalize_whitespace
from preprocessing.markdown_cleaner import clean_markdown
from preprocessing.confusable_normalizer import normalize_unicode_confusables
from preprocessing.homoglyph_normalizer import normalize_homoglyphs
from preprocessing.mixed_language_normalizer import normalize_mixed_language

def decode_once(prompt: str):
    changed = False

    prompt, unicode_flag = normalize_unicode(prompt)
    changed |= unicode_flag
    
    prompt, homoglyph_flag = normalize_homoglyphs(prompt)
    changed |= homoglyph_flag

    prompt, confusable_flag = normalize_unicode_confusables(prompt)
    changed |= confusable_flag

    prompt, markdown_flag = clean_markdown(prompt)
    changed |= markdown_flag
    
    prompt, whitespace_flag = normalize_whitespace(prompt)
    changed |= whitespace_flag

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

    prompt, repeated_char_flag = normalize_repeated_chars(prompt)
    changed |= repeated_char_flag
    
    prompt, leetspeak_flag = decode_leetspeak(prompt)
    changed |= leetspeak_flag

    prompt, ocr_flag = normalize_ocr(prompt)
    changed |= ocr_flag

    prompt, mixed_language_flag = normalize_mixed_language(prompt)
    changed |= mixed_language_flag

    return (
        prompt,
        changed,
        {
            "unicode_flag": unicode_flag,
            "homoglyph_flag": homoglyph_flag,
            "confusable_flag": confusable_flag,
            "markdown_flag": markdown_flag,
            "whitespace_flag": whitespace_flag,
            "base64_flag": base64_flag,
            "hex_flag": hex_flag,
            "url_flag": url_flag,
            "html_flag": html_flag,
            "zero_width_flag": zero_width_flag,
            "repeated_char_flag": repeated_char_flag,
            "leetspeak_flag": leetspeak_flag,
            "ocr_flag": ocr_flag,
            "mixed_language_flag": mixed_language_flag
        }
    )

def iterative_decode(prompt: str, max_iterations: int = 20):
    flags = {
        "unicode_flag": False,
        "homoglyph_flag": False,
        "confusable_flag": False,
        "markdown_flag": False,
        "whitespace_flag": False,
        "base64_flag": False,
        "hex_flag": False,
        "url_flag": False,
        "html_flag": False,
        "zero_width_flag": False,
        "repeated_char_flag": False,
        "leetspeak_flag": False,
        "ocr_flag": False,
        "mixed_language_flag": False
    }

    for _ in range(max_iterations):
        old_prompt = prompt
        prompt, changed, current_flags = decode_once(prompt)
        for key, value in current_flags.items():
            flags[key] |= value
        if prompt == old_prompt:
            break

    return {
        "prompt": prompt,
        "flags": flags
    }

def preprocess_prompt(prompt: str):
    result = iterative_decode(prompt)
    
    response = {
        "prompt": result["prompt"],
        "flags": result["flags"],
        
        "unicode_flag": result["flags"]["unicode_flag"],
        "homoglyph_flag": result["flags"]["homoglyph_flag"],
        "confusable_flag": result["flags"]["confusable_flag"],
        "markdown_flag": result["flags"]["markdown_flag"],
        "whitespace_flag": result["flags"]["whitespace_flag"],
        "base64_flag": result["flags"]["base64_flag"],
        "hex_flag": result["flags"]["hex_flag"],
        "url_flag": result["flags"]["url_flag"],
        "html_flag": result["flags"]["html_flag"],
        "zero_width_flag": result["flags"]["zero_width_flag"],
        "repeated_char_flag": result["flags"]["repeated_char_flag"],
        "leetspeak_flag": result["flags"]["leetspeak_flag"],
        "ocr_flag": result["flags"]["ocr_flag"],
        "mixed_language_flag": result["flags"]["mixed_language_flag"],
    }
    
    import logging, json
    from datetime import datetime, UTC
    logger = logging.getLogger("promptsentinel")
    logger.info(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "preprocessing_completed",
        "flags_changed": any(result["flags"].values())
    }))

    return response
