import os

from connectors.markdown_parser import extract_text as extract_markdown
from connectors.html_parser import extract_text as extract_html
from connectors.docx_parser import extract_text as extract_docx
from connectors.pdf_parser import extract_text as extract_pdf
from connectors.email_parser import extract_text as extract_email


def load_file(file_path: str):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".md":
        return extract_markdown(file_path)

    elif extension in [".html", ".htm"]:
        return extract_html(file_path)

    elif extension == ".pdf":
        return extract_pdf(file_path)

    elif extension == ".docx":
        return extract_docx(file_path)

    elif extension == ".eml":
        return extract_email(file_path)

    else:
        raise ValueError(f"Unsupported file type: {extension}")
