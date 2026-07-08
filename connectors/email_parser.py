from email import policy
from email.parser import BytesParser

from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)

from context.source import ScanSource


def parse_email(file_path: str) -> ExtractionResult:

    items = []

    with open(
        file_path,
        "rb"
    ) as file:

        message = BytesParser(
            policy=policy.default
        ).parse(file)


    # -----------------------
    # Subject
    # -----------------------

    subject = message.get("Subject")

    if subject:

        items.append(
            ExtractedContent(
                content=subject,
                source=ScanSource.EMAIL_SUBJECT
            )
        )


    # -----------------------
    # Headers
    # -----------------------

    headers = []

    for key, value in message.items():

        headers.append(
            f"{key}: {value}"
        )


    if headers:

        items.append(
            ExtractedContent(
                content="\n".join(headers),
                source=ScanSource.EMAIL_HEADER
            )
        )


    # -----------------------
    # Body
    # -----------------------

    if message.is_multipart():

        for part in message.walk():

            content_type = part.get_content_type()

            disposition = (
                part.get_content_disposition()
            )


            # Attachments
            if disposition == "attachment":

                filename = part.get_filename()

                if filename:

                    items.append(
                        ExtractedContent(
                            content=filename,
                            source=ScanSource.EMAIL_ATTACHMENT
                        )
                    )

                continue


            # Plain text
            if content_type == "text/plain":

                content = part.get_content()

                if content.strip():

                    items.append(
                        ExtractedContent(
                            content=content,
                            source=ScanSource.EMAIL_TEXT
                        )
                    )


            # HTML
            elif content_type == "text/html":

                content = part.get_content()

                if content.strip():

                    items.append(
                        ExtractedContent(
                            content=content,
                            source=ScanSource.EMAIL_HTML
                        )
                    )


    else:

        content_type = message.get_content_type()

        content = message.get_content()

        if content.strip():

            if content_type == "text/html":

                source = ScanSource.EMAIL_HTML

            else:

                source = ScanSource.EMAIL_TEXT


            items.append(
                ExtractedContent(
                    content=content,
                    source=source
                )
            )


    return ExtractionResult(
        items=items
    )
