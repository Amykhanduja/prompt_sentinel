import os

from connectors.email_parser import parse_email
from connectors.docx_parser import parse_docx
from connectors.pdf_parser import parse_pdf
from connectors.zip_parser import parse_zip
from connectors.extraction_result import ExtractionResult
from connectors.text_parser import parse_text
from connectors.markdown_parser import parse_markdown
from connectors.html_parser import parse_html
from context.source import ScanSource


PARSER_MAP = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".html": parse_html,
    ".htm": parse_html,
    ".zip": parse_zip,
    ".eml": parse_email,
    ".md": parse_markdown,
    ".markdown": parse_markdown,
    ".txt": parse_text,
    ".log": parse_text,
    ".csv": parse_text
}


MAX_DEPTH = 5


def recursive_load(
    file_path: str,
    depth: int = 0
):

    if depth > MAX_DEPTH:
        raise ValueError(
            "Maximum recursion depth exceeded"
        )


    extension = os.path.splitext(
        file_path
    )[1].lower()


    parser = PARSER_MAP.get(
        extension
    )


    if parser is None:

        return ExtractionResult(
            items=[]
        )


    result = parser(
        file_path
    )


    final_items = []


    for item in result.items:

        final_items.append(
            item
        )


        if (
            item.source == ScanSource.ZIP
            and os.path.isfile(item.content)
        ):


           try:
               nested = recursive_load(
                   item.content,
                   depth + 1
               )

               final_items.extend(
                   nested.items
               )
           except Exception:
                continue


    return ExtractionResult(
        items=final_items
    )
