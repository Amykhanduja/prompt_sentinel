from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)
from scan_source import ScanSource


def extract_pdf(file_path: str) -> ExtractionResult:
    """
    Extract all scannable contexts from a PDF.

    Current:
        - Visible text
        - Metadata

    Future:
        - Embedded files
        - Attachments
        - Forms
        - Annotations
    """

    items = []

    return ExtractionResult(items=items)
