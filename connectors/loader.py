import os

from connectors.markdown_parser import parse_markdown
from connectors.html_parser import parse_html
from connectors.docx_parser import parse_docx
from connectors.pdf_parser import parse_pdf
from connectors.email_parser import parse_email


def load_file(file_path: str):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".md":
        return parse_markdown(file_path)

    elif extension in [".html", ".htm"]:
        return parse_html(file_path)

    elif extension == ".pdf":
        return parse_pdf(file_path)

    elif extension == ".docx":
        return parse_docx(file_path)

    elif extension == ".eml":
        return parse_email(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )
