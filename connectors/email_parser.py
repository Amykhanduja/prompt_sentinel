from email import policy
from email.parser import BytesParser

from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)
from scan_source import ScanSource


def parse_email(file_path: str) -> ExtractionResult:

    with open(file_path, "rb") as file:
        message = BytesParser(policy=policy.default).parse(file)

    items = []

    text = ""

    if message.is_multipart():

        for part in message.walk():

            if part.get_content_type() == "text/plain":

                text += part.get_content()

    else:

        text = message.get_content()

    if text.strip():

        items.append(
            ExtractedContent(
                content=text,
                source=ScanSource.EMAIL
            )
        )

    return ExtractionResult(items=items)
