#!/usr/bin/env python
"""Minimal example of how to add a table to a text document."""

import os

from odfdo import Document, Header, Paragraph, Table

_DOC_SEQUENCE = 55


def generate_document() -> Document:
    """Return a document with a 3x3 table."""
    document = Document("text")
    body = document.body

    body.append(Header(1, "Tables"))
    body.append(Paragraph("A 3x3 table:"))

    # Creating a table :
    table = Table("Table name", width=3, height=3)
    body.append(table)
    return document


def main() -> None:
    document = generate_document()
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table = document.body.get_table(0)
    assert table.size == (3, 3)


if __name__ == "__main__":
    main()
