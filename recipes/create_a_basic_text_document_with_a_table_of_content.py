#!/usr/bin/env python
"""Create a basic text document with a table of content.
"""
import os
from pathlib import Path

from odfdo import TOC, Document, Header, Paragraph

_DOC_SEQUENCE = 35
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_toc"
DATA = Path(__file__).parent / "data"
LOREM = (DATA / "lorem.txt").read_text(encoding="utf8")
TARGET = "document.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = Document("text")
    make_toc(document)
    save_new(document, TARGET)


def make_toc(document):
    # Create the document
    body = document.body

    # Create the Table Of Content
    toc = TOC()
    # Changing the default "Table Of Content" Title :
    toc.title = "My Table of Content"

    # Do not forget to add the component to the document:
    body.append(toc)

    # Add some content with headers
    title1 = Header(1, LOREM[:70])
    body.append(title1)
    for idx in range(3):
        title = Header(2, LOREM[idx * 5 : 70 + idx * 5])
        body.append(title)
        paragraph = Paragraph(LOREM)
        body.append(paragraph)

    # Beware, update the TOC with the actual content. If not done there,
    # the reader will need to "update the table of content" later.
    toc.fill()

    # only for test suite:
    if "ODFDO_TESTING" in os.environ:
        assert str(toc).split("\n")[2] == (
            "1.1. Lorem ipsum dolor sit amet, consectetuer "
            "adipiscing elit. Sed non risu"
        )


if __name__ == "__main__":
    main()
