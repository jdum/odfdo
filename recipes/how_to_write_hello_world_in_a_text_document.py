#!/usr/bin/env python
"""Create a minimal text document with "Hello World" in a pragraph."""

import os
from pathlib import Path

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 3
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_hello"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_document() -> Document:
    document = Document("text")
    body = document.body
    body.clear()
    paragraph = Paragraph("Hello World")
    body.append(paragraph)

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    text = str(document.body)
    assert text == "Hello World\n"


if __name__ == "__main__":
    main()
