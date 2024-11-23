#!/usr/bin/env python
"""Copy the styles from an existing document.

For more advanced version, see the odfdo-style script.
"""
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 320
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"
# copied here from the odfdo package:
STYLE_SOURCE = DATA / "lpod_styles.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "styled1"
TARGET = "document.odt"


def read_source_document():
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    # We want to change the styles of collection2.odt,
    # we know the odfdo_styles.odt document contains an interesting style,
    # So let's first fetch the style:
    style_document = Document(STYLE_SOURCE)

    # Open our document:
    document = read_source_document()

    # We could change only some styles, but here we want a clean basis:
    document.delete_styles()

    # And now the actual style change:
    document.merge_styles_from(style_document)

    save_new(document, TARGET)


if __name__ == "__main__":
    main()
