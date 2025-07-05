#!/usr/bin/env python
"""Minimal example of how to add a sublist to a list."""

import os
from pathlib import Path

from odfdo import Document, List, ListItem

_DOC_SEQUENCE = 27
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "minimal_list"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_document() -> Document:
    """Return a text document with a list."""
    document = Document("text")
    body = document.body

    my_list = List(["chocolat", "café"])
    body.append(my_list)

    item = ListItem("thé")
    my_list.append(item)

    # A sublist is simply a list as an item of another list
    item.append(List(["thé vert", "thé rouge"]))

    print(body.serialize(True))

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(document.body.get_lists()) == 2


if __name__ == "__main__":
    main()
