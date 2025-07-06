#!/usr/bin/env python
"""Search and replace words in a text document."""

import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 700
DATA = Path(__file__).parent / "data"
SOURCE = "lorem.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "replaced_text"
TARGET = "lorem_replaced.odt"


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


def search_replace(document: Document) -> None:
    body = document.body

    # replace a string in the full document
    body.replace("Lorem", "(Lorem replaced)")

    # replace in paragraphs only
    for paragraph in body.paragraphs:
        paragraph.replace("ipsum", "(ipsum in paragraph)")

    # replace in headers
    for header in body.headers:
        header.replace("ipsum", "(ipsum in header)")

    # pattern is a regular expression
    body.replace(r"\S+lit ", "(...lit) ")
    body.replace(r"pul[a-z]+", "(pulvinar)")


def main() -> None:
    document = read_source_document()
    search_replace(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    body = document.body
    assert len(body.search_all("replaced")) == 3
    assert len(body.search_all("(pulvinar)")) == 2


if __name__ == "__main__":
    main()
