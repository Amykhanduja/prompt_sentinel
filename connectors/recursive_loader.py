import os

from connectors.loader import load_file
from connectors.zip_parser import extract_files

from context.source import ScanSource


MAX_DEPTH = 5


def recursive_load(file_path: str, depth: int = 0):

    if depth >= MAX_DEPTH:
        raise RecursionError(
            f"Maximum recursion depth ({MAX_DEPTH}) exceeded."
        )

    extension = os.path.splitext(file_path)[1].lower()

    # ZIP archives
    if extension == ".zip":

        text = ""

        extracted_files = extract_files(file_path)

        for extracted_file in extracted_files:

            result = recursive_load(
                extracted_file,
                depth + 1
            )

            extracted_text = result["text"]

            if extracted_text.strip():

                text += extracted_text
                text += "\n\n"

        return {
            "text": text.strip(),
            "source": ScanSource.ZIP
        }

    # Every other supported file

    return load_file(file_path)

