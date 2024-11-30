#!/usr/bin/env python
"""Create a basic spreadsheet with "Hello World" in the first cell.
"""
import os
from pathlib import Path

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 3
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_hello"
TARGET = "document.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = Document("text")
    body = document.body
    body.clear()
    paragraph = Paragraph("Hello World")
    body.append(paragraph)

    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    text = str(document.body)
    print(text)
    assert text == "Hello World\n"


if __name__ == "__main__":
    main()
