#!/usr/bin/env python
"""Create an empty text document and add a list.
"""
import os
from pathlib import Path

# Lists are a dedicated object List
from odfdo import Document, List

_DOC_SEQUENCE = 90
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "add_list"
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
    some_list = List(["chocolate", "tea", "coffee"])
    # The list factory accepts a Python list of strings and list items.
    body.append(some_list)

    test_unit(document)

    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    assert (document.get_formatted_text()).strip() == "- chocolate\n- tea\n- coffee"


if __name__ == "__main__":
    main()
