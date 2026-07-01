from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)
from scan_source import ScanSource


def parse_markdown(file_path: str) -> ExtractionResult:

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    items = []

    if text.strip():
        items.append(
            ExtractedContent(
                content=text,
                source=ScanSource.MARKDOWN
            )
        )

    return ExtractionResult(items=items)
