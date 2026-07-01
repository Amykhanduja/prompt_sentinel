import os

from connectors.loader import load_file
from connectors.zip_parser import extract_files
from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)


MAX_DEPTH = 5


def recursive_load(file_path: str, depth: int = 0) -> ExtractionResult:

    if depth >= MAX_DEPTH:
        raise RecursionError(
            f"Maximum recursion depth ({MAX_DEPTH}) exceeded."
        )

    extension = os.path.splitext(file_path)[1].lower()

    # ZIP archives
    if extension == ".zip":

        items = []

        extracted_files = extract_files(file_path)

        for extracted_file in extracted_files:

            result = recursive_load(
                extracted_file,
                depth + 1
            )

            items.extend(result.items)

        return ExtractionResult(items=items)

    # Every other supported file

    return load_file(file_path)
