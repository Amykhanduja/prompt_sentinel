from docx import Document

from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)
from scan_source import ScanSource


def parse_docx(file_path: str) -> ExtractionResult:

    document = Document(file_path)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )

    items = []

    if text.strip():
        items.append(
            ExtractedContent(
                content=text,
                source=ScanSource.DOCX
            )
        )

    return ExtractionResult(items=items)
