from bs4 import (
    BeautifulSoup,
    Comment,
)

from connectors.extraction_result import (
    ExtractionResult,
    ExtractedContent,
)

from context.source import ScanSource


def parse_html(file_path: str) -> ExtractionResult:

    items = []

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        html = file.read()


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    # -----------------------
    # Visible text
    # -----------------------

    visible_text = soup.get_text(
        separator=" ",
        strip=True
    )

    if visible_text:

        items.append(
            ExtractedContent(
                content=visible_text,
                source=ScanSource.HTML
            )
        )


    # -----------------------
    # HTML comments
    # -----------------------

    comments = []

    for comment in soup.find_all(
        string=lambda text: isinstance(
            text,
            Comment
        )
    ):

        if comment.strip():

            comments.append(
                str(comment)
            )


    if comments:

        items.append(
            ExtractedContent(
                content="\n".join(comments),
                source=ScanSource.HTML_COMMENT
            )
        )


    # -----------------------
    # Meta tags
    # -----------------------

    metadata = []

    for meta in soup.find_all("meta"):

        name = (
            meta.get("name")
            or meta.get("property")
        )

        content = meta.get("content")

        if name and content:

            metadata.append(
                f"{name}: {content}"
            )


    if metadata:

        items.append(
            ExtractedContent(
                content="\n".join(metadata),
                source=ScanSource.HTML_METADATA
            )
        )


    # -----------------------
    # Scripts
    # -----------------------

    scripts = []

    for script in soup.find_all("script"):

        if script.string:

            scripts.append(
                script.string
            )


    if scripts:

        items.append(
            ExtractedContent(
                content="\n".join(scripts),
                source=ScanSource.HTML_SCRIPT
            )
        )


    # -----------------------
    # Styles
    # -----------------------

    styles = []

    for style in soup.find_all("style"):

        if style.string:

            styles.append(
                style.string
            )


    if styles:

        items.append(
            ExtractedContent(
                content="\n".join(styles),
                source=ScanSource.HTML_STYLE
            )
        )


    # -----------------------
    # Hidden elements
    # -----------------------

    hidden = []

    for tag in soup.find_all(True):

        style = (
            tag.get("style", "")
            .replace(" ", "")
            .lower()
        )

        if (
            tag.has_attr("hidden")
            or "display:none" in style
            or "visibility:hidden" in style
        ):

            text = tag.get_text(
                separator=" ",
                strip=True
            )

            if text:

                hidden.append(
                    text
                )


    if hidden:

        items.append(
            ExtractedContent(
                content="\n".join(hidden),
                source=ScanSource.HTML_HIDDEN
            )
        )


    return ExtractionResult(
        items=items
    )

def extract_text(file_path: str) -> str:
    res = parse_html(file_path)
    return res.items[0].content if res.items else ""
