from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)

from context.source import ScanSource


def parse_markdown(file_path: str) -> ExtractionResult:

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
                source=ScanSource.MARKDOWN
            )
        )


    return ExtractionResult(
        items=items
    )

def extract_text(file_path: str) -> str:
    res = parse_markdown(file_path)
    return res.items[0].content if res.items else ""
