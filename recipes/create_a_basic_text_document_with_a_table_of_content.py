#!/usr/bin/env python
"""Create a basic document containing some paragraphs and headers, add a
Table of Content from its headers.
"""

import os
from pathlib import Path

from odfdo import TOC, Document, Header, Paragraph

_DOC_SEQUENCE = 35
DATA = Path(__file__).parent / "data"
LOREM = (DATA / "lorem.txt").read_text(encoding="utf8")
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_toc"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def make_document() -> Document:
    """Generate a basic document containing some paragraphs and headers."""
    document = Document("text")
    body = document.body
    body.clear()

    level_1_title = Header(1, LOREM[:70])
    body.append(level_1_title)

    for idx in range(3):
        level_2_title = Header(2, LOREM[idx * 5 : 70 + idx * 5])
        body.append(level_2_title)
        paragraph = Paragraph(LOREM)
        body.append(paragraph)

    return document


def add_toc(document: Document) -> None:
    """Add a Table of Content to the document from its headers."""
    # Create the Table Of Content
    toc = TOC()
    # Changing the default "Table Of Content" Title :
    toc.title = "My Table of Content"

    # If the TOC is append to document, it will appera at the end:
    # document.body.append(toc)
    #
    # So we prefer to insert it at top of document:
    document.body.insert(toc, position=0)

    # Beware, update the TOC with the actual content. If not done there,
    # the reader will need to "update the table of content" later.
    toc.fill()


def main() -> None:
    document = make_document()
    add_toc(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    toc = document.body.get_toc()
    assert str(toc).split("\n")[2] == (
        "1.1. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Sed non risu"
    )
    position = document.body.index(toc)
    assert position == 0


if __name__ == "__main__":
    main()
