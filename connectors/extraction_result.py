from dataclasses import dataclass

from context.source import ScanSource


@dataclass
class ExtractedContent:

    content: str
    source: ScanSource



@dataclass
class ExtractionResult:

    items: list[ExtractedContent]
