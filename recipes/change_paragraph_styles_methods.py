#!/usr/bin/env python
"""Many examples of how to change paragraph (and in-paragraph) styles, either
by changing the paragraph style itself or by using Span to select parts
of the paragraph. Includes several ways to create or import styles.
"""

import os
from collections.abc import Iterator
from itertools import cycle
from pathlib import Path

from odfdo import Document, Element, Header, Paragraph, Style

_DOC_SEQUENCE = 340
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "change_styles"
DATA = Path(__file__).parent / "data"
LOREM = (DATA / "lorem.txt").read_text(encoding="utf8")
STYLED_SOURCE = "lpod_styles.odt"
TARGET_BEFORE = "document_before.odt"
TARGET_AFTER = "document_after.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def iter_lorem() -> Iterator[str]:
    """Return infinite iterator on Lorem Ipsum content."""
    return cycle(lr.strip() for lr in LOREM.replace("\n", " ").split("."))


def make_base_document() -> Document:
    """Generate document from parts of lorem ipsum content."""
    document = Document("odt")
    body = document.body
    body.clear()
    # Add some content with headers
    lorem = iter_lorem()
    title1 = Header(1, next(lorem))
    body.append(title1)
    for _i in range(3):
        title = Header(2, next(lorem))
        body.append(title)
        for _j in range(5):
            body.append(Paragraph(next(lorem) + ". " + next(lorem) + "."))
    return document


def add_some_styles(document) -> None:
    """Add programmatically generated styles to the document."""
    # Always simpler to copy styles from an actual .odt existing file, but:
    document.insert_style(
        Style(
            family="paragraph",
            area="text",
            display_name="bold-blue",
            color="blue",
            bold=True,
        ),
        automatic=True,
    )
    document.insert_style(
        Style(
            family="paragraph",
            area="text",
            display_name="italic-red",
            color="red",
            bold=True,
            italic=True,
        ),
        automatic=True,
    )
    document.insert_style(
        Style(
            family="text",
            area="text",
            display_name="green",
            background_color="green",
        ),
        automatic=True,
    )
    document.insert_style(
        Style(
            family="text",
            area="text",
            display_name="bold-yellow-blue",
            color="yellow",
            background_color="blue",
            bold=True,
        ),
        automatic=True,
    )
    document.insert_style(
        Style(
            family="text",
            area="text",
            display_name="bold-white-black",
            color="white",
            background_color="black",
            bold=True,
        ),
        automatic=True,
    )
    document.insert_style(
        Style(
            family="text",
            area="text",
            display_name="italic-red-yellow",
            color="red",
            background_color="yellow",
            bold=True,
            italic=True,
        ),
        automatic=True,
    )


def add_style_from_xml(document: Document) -> None:
    """Add styles defined by XML content to the document."""
    # Styles can be defined by WML definition
    document.insert_style(
        Element.from_tag(
            '<style:style style:name="custom" '
            'style:display-name="custom" '
            'style:family="paragraph" '
            'style:parent-style-name="Text">'
            '<style:paragraph-properties fo:margin-left="2cm"/>'
            '<style:text-properties fo:color="#808080" loext:opacity="100%" '
            'fo:font-size="16pt" fo:font-style="normal" '
            'style:text-underline-style="solid" '
            'style:text-underline-width="auto" '
            'style:text-underline-color="font-color" '
            'fo:font-weight="bold"/>'
            "</style:style>"
        )
    )


def import_style_from_other_doc(document: Document) -> None:
    """Add styles imported from another document to the document."""
    styled_doc = Document(DATA / STYLED_SOURCE)
    highlight = styled_doc.get_style("text", display_name="Yellow Highlight")
    document.insert_style(highlight, automatic=True)


def apply_styles(document: Document) -> None:
    """Apply some style changes to the document."""

    def change_all_headers() -> None:
        style = document.get_style(family="text", display_name="green")
        # header styles should include some hints about he numeration level
        # So, here we just prefer to apply style with a span
        for header in document.body.headers:
            header.set_span(style.name, offset=0)

    def change_all_paragraphs() -> None:
        style = document.get_style(family="paragraph", display_name="bold-blue")
        for para in document.body.paragraphs:
            para.style = style.name

    def change_some_paragraph() -> None:
        style = document.get_style(family="paragraph", display_name="italic-red")
        document.body.get_paragraph(3).style = style.name
        document.body.get_paragraph(5).style = style.name
        document.body.get_paragraph(7).style = style.name

    def apply_span_regex() -> None:
        yellow = document.get_style(family="text", display_name="bold-yellow-blue")
        white = document.get_style(family="text", display_name="bold-white-black")
        for para in document.body.paragraphs:
            para.set_span(yellow.name, regex=r"tortor|ipsum")
            para.set_span(white.name, regex=r"A\w+")

    def apply_span_offset() -> None:
        red = document.get_style(family="text", display_name="italic-red-yellow")
        para = document.body.get_paragraph(2)
        para.set_span(red.name, offset=9, length=22)

    def apply_custom_style() -> None:
        para = document.body.get_paragraph(13)
        para.style = "custom"

    def apply_imported_style() -> None:
        para = document.body.get_paragraph(14)
        style = document.get_style(family="text", display_name="Yellow Highlight")
        # feature: to not highlight spaces, make as many Spans as required:
        for start, end in para.search_all(r"\w+"):
            length = end - start
            para.set_span(style.name, offset=start, length=length)

    change_all_headers()
    change_all_paragraphs()
    change_some_paragraph()
    apply_span_regex()
    apply_span_offset()
    apply_custom_style()
    apply_imported_style()


def main() -> None:
    document = make_base_document()
    save_new(document, TARGET_BEFORE)
    add_some_styles(document)
    add_style_from_xml(document)
    import_style_from_other_doc(document)
    apply_styles(document)
    test_unit(document)
    save_new(document, TARGET_AFTER)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(list(document.body.paragraphs)) == 15
    for display_name in (
        "bold-blue",
        "italic-red",
        "custom",
    ):
        style = document.get_style(family="paragraph", display_name=display_name)
        assert document.get_styled_elements(style.name)
    for display_name in (
        "green",
        "bold-yellow-blue",
        "bold-white-black",
        "Yellow Highlight",
    ):
        style = document.get_style(family="text", display_name=display_name)
        assert document.get_styled_elements(style.name)
    style = document.get_style(family="text", display_name="Yellow Highlight")
    assert len(document.get_styled_elements(style.name)) == 21


if __name__ == "__main__":
    main()
