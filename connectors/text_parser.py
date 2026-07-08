from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)

from context.source import ScanSource


def parse_text(file_path: str) -> ExtractionResult:

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        text = file.read()


    items = []

    if text.strip():

        items.append(
            ExtractedContent(
                content=text,
                source=ScanSource.TEXT
            )
        )


    return ExtractionResult(
        items=items
    )
