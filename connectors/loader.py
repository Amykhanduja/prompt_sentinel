import os

from context.source import ScanSource

from connectors.markdown_parser import extract_text as extract_markdown
from connectors.html_parser import extract_text as extract_html
from connectors.docx_parser import extract_text as extract_docx
from connectors.pdf_parser import extract_text as extract_pdf
from connectors.email_parser import extract_text as extract_email


def load_file(file_path: str):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".md":

        return {
            "text": extract_markdown(file_path),
            "source": ScanSource.USER
        }

    elif extension in [".html", ".htm"]:

        return {
            "text": extract_html(file_path),
            "source": ScanSource.HTML
        }

    elif extension == ".pdf":

        return {
            "text": extract_pdf(file_path),
            "source": ScanSource.PDF
        }

    elif extension == ".docx":

        return {
            "text": extract_docx(file_path),
            "source": ScanSource.DOCX
        }

    elif extension == ".eml":

        return {
            "text": extract_email(file_path),
            "source": ScanSource.EMAIL
        }

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )
