import fitz

from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)

from context.source import ScanSource


def parse_pdf(file_path: str) -> ExtractionResult:

    document = fitz.open(file_path)

    items = []

    try:

        # -------------------------
        # 1. Visible PDF Text
        # -------------------------

        text = ""

        for page in document:
            page_text = page.get_text()

            if page_text:
                text += page_text + "\n"

        if text.strip():

            items.append(
                ExtractedContent(
                    content=text.strip(),
                    source=ScanSource.PDF
                )
            )


        # -------------------------
        # 2. PDF Metadata
        # -------------------------

        metadata = document.metadata

        if metadata:

            metadata_text = ""

            for key, value in metadata.items():

                if value:
                    metadata_text += (
                        f"{key}: {value}\n"
                    )

            if metadata_text.strip():

                items.append(
                    ExtractedContent(
                        content=metadata_text.strip(),
                        source=ScanSource.PDF_METADATA
                    )
                )


        # -------------------------
        # 3. Embedded Files
        # -------------------------
        
        import os
        import tempfile

        if document.embfile_count() > 0:
            temp_dir = tempfile.mkdtemp()

            for name in document.embfile_names():

                try:

                    embedded = document.embfile_get(
                        name
                    )

                    if isinstance(
                        embedded,
                        bytes
                    ):
                        
                        filepath = os.path.join(temp_dir, name)
                        with open(filepath, "wb") as f:
                            f.write(embedded)

                        items.append(
                            ExtractedContent(
                                content=filepath,
                                source=ScanSource.PDF_EMBEDDED
                            )
                        )

                except Exception:

                    continue


        # -------------------------
        # 4. Annotations
        # -------------------------

        annotation_text = ""

        for page in document:

            annotations = page.annots()

            if annotations:

                for annotation in annotations:

                    info = annotation.info

                    if info:

                        content = info.get(
                            "content",
                            ""
                        )

                        title = info.get(
                            "title",
                            ""
                        )

                        if title:
                            annotation_text += (
                                f"Title: {title}\n"
                            )

                        if content:
                            annotation_text += (
                                f"Content: {content}\n"
                            )


        if annotation_text.strip():

            items.append(
                ExtractedContent(
                    content=annotation_text.strip(),
                    source=ScanSource.PDF
                )
            )


        # -------------------------
        # 5. Form Fields
        # -------------------------

        if document.is_form_pdf:

            form_text = ""

            for page in document:

                widgets = page.widgets()

                if widgets:

                    for widget in widgets:

                        if widget.field_name:

                            form_text += (
                                f"{widget.field_name}: "
                                f"{widget.field_value}\n"
                            )


            if form_text.strip():

                items.append(
                    ExtractedContent(
                        content=form_text.strip(),
                        source=ScanSource.PDF
                    )
                )


    finally:

        document.close()


    return ExtractionResult(
        items=items
    )

def extract_text(file_path: str) -> str:
    res = parse_pdf(file_path)
    return res.items[0].content if res.items else ""
