import urllib.parse


def decode_url_content(text: str):

    decoded = urllib.parse.unquote(text)

    decoded_flag = decoded != text

    return decoded, decoded_flag
