#!/usr/bin/env python
"""Create a basic text document with list and sublists.
"""
import os
from pathlib import Path

from odfdo import Document, List, ListItem

_DOC_SEQUENCE = 25
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_sublist"
TARGET = "document.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def generate_document():
    document = Document("text")
    body = document.body

    # Adding List
    name_list = List(["Arthur", "Ford", "Trillian"])
    item = ListItem("Marvin")
    name_list.append_item(item)
    body.append(name_list)

    # Adding Sublist¶
    # A sublist is simply a list as an item of another list:
    item.append(List(["Paranoid Android", "older than the universe"]))

    # See the result:
    print(document.get_formatted_text())
    # - Arthur
    # - Ford
    # - Trillian
    # - Marvin
    #   - Paranoid Android
    #   - older than the universe

    # Inserting List Item
    # In case your forgot to insert an item:
    name_list.insert_item("some dolphins", position=1)

    # Or you can insert it before another item:
    marvin = name_list.get_item(content="Marvin")
    name_list.insert_item("Zaphod", before=marvin)
    # Or after:
    name_list.insert_item("and many others", after=marvin)

    # See the result:
    print(document.get_formatted_text())
    # - Arthur
    # - some dolphins
    # - Ford
    # - Trillian
    # - Zaphod
    # - Marvin
    #   - Paranoid Android
    #   - older than the universe
    # - and many others
    #

    return document


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    assert document.get_formatted_text().strip() == (
        "- Arthur\n"
        "- some dolphins\n"
        "- Ford\n"
        "- Trillian\n"
        "- Zaphod\n"
        "- Marvin\n"
        "  \n"
        "  - Paranoid Android\n"
        "  - older than the universe\n"
        "- and many others"
    )


if __name__ == "__main__":
    main()
