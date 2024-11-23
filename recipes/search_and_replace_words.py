#!/usr/bin/env python
"""Search and replace words in a text document.
"""
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 700
DATA = Path(__file__).parent / "data"
SOURCE = "lorem.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "replaced_text"
TARGET = "lorem_replaced.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def search_replace(document):
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


def main():
    document = Document(DATA / SOURCE)
    search_replace(document)
    save_new(document, TARGET)


if __name__ == "__main__":
    main()
