import os
import tempfile
import zipfile

from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)

from context.source import ScanSource


MAX_FILES = 100
MAX_TOTAL_SIZE = 100 * 1024 * 1024


def parse_zip(file_path: str) -> ExtractionResult:

    if not zipfile.is_zipfile(file_path):
        raise ValueError("Invalid ZIP file.")

    items = []

    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(file_path, "r") as archive:

        members = archive.infolist()


        # -----------------------
        # Safety checks
        # -----------------------

        if len(members) > MAX_FILES:
            raise ValueError(
                "ZIP contains too many files."
            )


        total_size = sum(
            member.file_size
            for member in members
        )


        if total_size > MAX_TOTAL_SIZE:
            raise ValueError(
                "ZIP exceeds maximum allowed size."
            )


        # -----------------------
        # Metadata
        # -----------------------

        for member in members:

            items.append(
                ExtractedContent(
                    content=member.filename,
                    source=ScanSource.ZIP
                )
            )


            if member.comment:

                items.append(
                    ExtractedContent(
                        content=member.comment.decode(
                            errors="ignore"
                        ),
                        source=ScanSource.ZIP
                    )
                )


        # -----------------------
        # Extraction
        # -----------------------

        for member in members:

            destination = os.path.abspath(
                os.path.join(
                    temp_dir,
                    member.filename
                )
            )


            if not destination.startswith(
                os.path.abspath(temp_dir)
            ):
                raise ValueError(
                    "Unsafe ZIP archive (Zip Slip detected)."
                )


            archive.extract(
                member,
                temp_dir
            )


    # -----------------------
    # Return extracted paths
    # recursive loader handles parsing
    # -----------------------

    for root, _, files in os.walk(temp_dir):

        for file in files:

            extracted_path = os.path.join(
                root,
                file
            )


            items.append(
                ExtractedContent(
                    content=extracted_path,
                    source=ScanSource.ZIP
                )
            )


    return ExtractionResult(
        items=items
    )
