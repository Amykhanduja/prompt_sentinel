import html


def decode_html_entities(text: str):

    decoded = html.unescape(text)

    decoded_flag = decoded != text

    return decoded, decoded_flag
