#!/usr/bin/env python
"""Create a minimal spreadsheet with "Hello World" in the first cell."""

import os
from pathlib import Path

from odfdo import Document, Table

_DOC_SEQUENCE = 5
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_ods"
TARGET = "document.ods"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_document() -> Document:
    document = Document("spreadsheet")
    body = document.body
    body.clear()

    table = Table("Hello table")
    table.set_value("A1", "Hello World")
    body.append(table)

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    text = document.body.get_table(0).get_cell((0, 0)).value.strip()
    print(text)
    assert text == "Hello World"


if __name__ == "__main__":
    main()
