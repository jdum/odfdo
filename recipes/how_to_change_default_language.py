#!/usr/bin/env python
"""Change the default language of a document, both in metadata and default styles."""

import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 11
DATA = Path(__file__).parent / "data"
SOURCE = "lorem.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "language_text"
TARGET = "lorem_en_us.odt"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def change_language(document: Document) -> None:
    current_language = document.language
    print(f"Current default language: {current_language!r}")

    document.language = "en-US"
    new_language = document.language
    print(f"New default language: {new_language!r}")


def main() -> None:
    document = read_source_document()
    change_language(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert document.language == "en-US"


if __name__ == "__main__":
    main()
