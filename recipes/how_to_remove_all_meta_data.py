#!/usr/bin/env python
"""Create a document with metadata, then remove all metadata,
including user defined fields."""

import os
from pathlib import Path

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 525
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "metadata"
WITH_METADATA = "with_metadata.odt"
NO_METADATA = "no_metadata.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_document() -> Document:
    """Return a document with some metadata and user defined fields."""
    document = Document("text")
    body = document.body
    body.clear()
    body.append(Paragraph("A small paragraph."))
    meta = document.meta
    meta.title = "The title of the document"
    meta.description = "Some description"
    meta.subject = "A very complex subject"
    meta.language = "en-US"
    meta.creator = "John Doe"
    meta.editing_cycles = 42
    meta.set_user_defined_metadata("Reference", "ABC-1234")
    meta.set_user_defined_metadata("Short Document", True)
    meta.set_user_defined_metadata("Version", 15)
    return document


def remove_meta(document: Document) -> None:
    """Return a copy of the document with metadata removed."""
    print("Display original metadata:")
    print(document.meta.as_json(full=False))

    document.meta.strip()

    print("Display cleaned document:")
    print(document.meta.as_json(full=False))


def main() -> None:
    document = generate_document()
    save_new(document, WITH_METADATA)
    remove_meta(document)
    save_new(document, NO_METADATA)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    meta = document.meta
    assert meta.title is None
    assert meta.description is None
    assert meta.subject is None
    assert meta.language is None
    assert meta.creator is None
    assert meta.editing_cycles == 1
    assert not meta.user_defined_metadata


if __name__ == "__main__":
    main()
