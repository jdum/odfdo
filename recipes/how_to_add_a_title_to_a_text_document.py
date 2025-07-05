#!/usr/bin/env python
"""Minimal example of how to add a Header of first level to a text document."""

import os

from odfdo import Document, Header

_DOC_SEQUENCE = 67


def generate_document() -> Document:
    """Return a document with a title."""
    document = Document("text")

    title1 = Header(1, "The Title")
    document.body.append(title1)

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    title = document.body.get_header(0)
    assert str(title).strip() == "The Title"


if __name__ == "__main__":
    main()
