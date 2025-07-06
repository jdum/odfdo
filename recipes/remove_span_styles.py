#!/usr/bin/env python
"""Remove span styles (like some words in bold in a paragraph),
except in titles.
"""

import os
import sys
from pathlib import Path

from odfdo import Document, Header, Span, remove_tree

_DOC_SEQUENCE = 520
DATA = Path(__file__).parent / "data"
SOURCE = "dormeur.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "nostyle"
TARGET = "document.odt"


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


def remove_all_text_span(document: Document) -> None:
    """Remove all span styles from a Document, except in titles."""
    body = document.body

    print("source, 'text:span' occurrences:", len(body.spans))
    remove_tree(document.body, Span, Header)
    print("final, 'text:span' occurrences after removal:", len(body.spans))


def main() -> None:
    document = read_source_document()
    remove_all_text_span(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(document.body.spans) == 1


if __name__ == "__main__":
    main()
