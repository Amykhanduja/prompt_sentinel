from bs4 import BeautifulSoup

from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)
from scan_source import ScanSource


def parse_html(file_path: str) -> ExtractionResult:

    with open(file_path, "r", encoding="utf-8") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    items = []

    if text.strip():
        items.append(
            ExtractedContent(
                content=text,
                source=ScanSource.HTML
            )
        )

    return ExtractionResult(items=items)

