#!/usr/bin/env python
"""Adding a manual page break to a text document.

Page breaks are build by a specific style. However, odfdo provides a PageBreak
class to facilitate the inclusion of page breaks. This recipe illustrates
the use of PageBreak and the underlying styling mechanism.
"""

import os
from pathlib import Path

from odfdo import Document, PageBreak, Paragraph, Style

_DOC_SEQUENCE = 95
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "page_break"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_document() -> Document:
    """Return a text document containing page breaks."""
    document = Document()
    body = document.body
    body.clear()

    # here a simple way to insert a page break with odfdoshortcuts:
    document.add_page_break_style()
    body.append(Paragraph("First paragraph"))
    body.append(PageBreak())
    body.append(Paragraph("Second paragraph"))

    # here is a different way to insert a page break:
    page_break_style = Style("paragraph", name="page_break_before")
    page_break_style.set_properties({"fo:break-before": "page"})
    document.insert_style(page_break_style)
    empty_paragraph = Paragraph("", style="page_break_before")
    body.append(empty_paragraph)
    body.append(Paragraph("Third paragraph"))

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    content = document.body.serialize(pretty=True)
    assert "First paragraph" in content
    assert "Second paragraph" in content
    assert "Third paragraph" in content
    assert '<text:p text:style-name="odfdopagebreak"></text:p>' in content
    assert '<text:p text:style-name="page_break_before"></text:p>' in content


if __name__ == "__main__":
    main()
