#!/usr/bin/env python
"""Create a basic text document with a list."""

import os
from pathlib import Path

from odfdo import Document, List, ListItem

_DOC_SEQUENCE = 20
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_list"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_document() -> Document:
    """Generate a basic text document with a list."""
    # Create the document
    document = Document("text")
    body = document.body

    # Adding List
    my_list = List(["Arthur", "Ford", "Trillian"])
    # The list accepts a Python list of strings and list items.

    # The list can be written even though we will modify it afterwards:
    body.append(my_list)

    # Adding more List Item to the list
    item = ListItem("Marvin")
    my_list.append_item(item)

    # it should contain:
    print(document.get_formatted_text())
    # - Arthur
    # - Ford
    # - Trillian
    # - Marvin

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert str(document).strip() == "- Arthur\n- Ford\n- Trillian\n- Marvin"


if __name__ == "__main__":
    main()
