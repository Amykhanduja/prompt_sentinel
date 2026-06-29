import fitz


def extract_text(file_path: str):

    document = fitz.open(file_path)

    text = ""

    for page in document:

        text += page.get_text()

    document.close()

    return text
