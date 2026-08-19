import os

from connectors.markdown_parser import parse_markdown
from connectors.html_parser import parse_html
from connectors.docx_parser import parse_docx
from connectors.pdf_parser import parse_pdf
from connectors.email_parser import parse_email


def load_file(file_path: str):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".md":
        res = parse_markdown(file_path)
    elif extension in [".html", ".htm"]:
        res = parse_html(file_path)
    elif extension == ".pdf":
        res = parse_pdf(file_path)
    elif extension == ".docx":
        res = parse_docx(file_path)
    elif extension == ".eml":
        res = parse_email(file_path)
    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if hasattr(res, "items") and res.items:
        source = res.items[0].source
        from context.source import ScanSource
        if extension in [".md", ".markdown"]:
            source = ScanSource.USER
        return {
            "text": res.items[0].content,
            "source": source
        }
    return res
