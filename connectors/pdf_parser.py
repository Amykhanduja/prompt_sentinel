import fitz

from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)
from scan_source import ScanSource


def parse_pdf(file_path: str) -> ExtractionResult:

    document = fitz.open(file_path)

    items = []

    text = ""

    for page in document:
        text += page.get_text()

    if text.strip():
        items.append(
            ExtractedContent(
                content=text,
                source=ScanSource.PDF
            )
        )

    document.close()

    return ExtractionResult(items=items)
