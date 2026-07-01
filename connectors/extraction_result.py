from dataclasses import dataclass
from scan_source import ScanSource


@dataclass
class ExtractedContent:
    content: str
    source: ScanSource


@dataclass
class ExtractionResult:
    items: list[ExtractedContent]
