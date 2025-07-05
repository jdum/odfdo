#!/usr/bin/env python
"""Read the text content from an .odt file."""

import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 30
DATA = Path(__file__).parent / "data"
# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA) :
SOURCE = "collection2.odt"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def read_text_content(document: Document) -> str:
    """Return the text content of the document."""
    # just verify what type of document it is:
    print("Type of document:", document.get_type())
    # A quick way to get the text content:
    text = document.get_formatted_text()

    print("Size of text:", len(text))

    # Let's show the beginning :
    print("Start of the text:")
    print(text[:240])

    return text


def main() -> None:
    document = read_source_document()
    text = read_text_content(document)
    test_unit(text)


def test_unit(text: str) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(text) == 56828


if __name__ == "__main__":
    main()
