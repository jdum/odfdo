#!/usr/bin/env python
"""Minimal example of how to add a styled paragraph to a document."""

import os

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 335


def generate_document() -> Document:
    """Return a document with some styled paragraph"""
    document = Document("text")
    body = document.body
    body.clear()

    # Assuming we have a style of name "highlight" :
    body.append(Paragraph("Highlighting the word", style="highlight"))

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    paragraphs = document.body.paragraphs
    assert len(paragraphs) == 1
    assert paragraphs[0].style == "highlight"


if __name__ == "__main__":
    main()
