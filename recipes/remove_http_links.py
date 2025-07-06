#!/usr/bin/env python
"""Remove all the links (the text:a tag), keeping the inner text."""

import os
import sys
from pathlib import Path
from typing import Any

from odfdo import Document, Element

_DOC_SEQUENCE = 510
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "nolink"
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


def sub_tree_remove_tag(
    element: Element,
    context: dict[str, Any],
) -> tuple[list, bool]:
    """Remove tag in the children of the element."""
    modified = False
    sub_elements = []
    for child in element.children:
        striped, is_modified = tree_remove_tag(child, context)
        if is_modified:
            modified = True
        if isinstance(striped, list):
            sub_elements.extend(striped)
        else:
            sub_elements.append(striped)
    return sub_elements, modified


def tree_remove_tag(
    element: Element,
    context: dict[str, Any],
) -> tuple[list | Element, bool]:
    """Remove tag in the element, recursive.

    Context argument contains: tag to remove, protection tag, protection flag.
    Protection tag protect from change sub elements one sub level depth.
    """
    buffer = element.clone
    tag = context["tag"]
    protect_tag = context["protect_tag"]
    protected = context["protected"]
    if element.tag == protect_tag and protected:
        protect_below = True
    else:
        protect_below = False
    sub_context: dict[str, Any] = {
        "tag": tag,
        "protect_tag": protect_tag,
        "protected": protect_below,
    }
    sub_elements, modified = sub_tree_remove_tag(buffer, sub_context)
    if element.tag == tag and not protected:
        list_element = []
        text = buffer.text
        tail = buffer.tail
        if text is not None:
            list_element.append(text)
        list_element.extend(sub_elements)
        if tail is not None:
            list_element.append(tail)
        return list_element, True
    if not modified:
        # no change in element sub tree, no change on element
        return element, False
    element.clear()
    try:
        for key, value in buffer.attributes.items():
            element.set_attribute(key, value)
    except ValueError:
        print(f"Incorrect attribute in {buffer}")
    text = buffer.text
    tail = buffer.tail
    if text is not None:
        element.append(text)
    for elem in sub_elements:
        element.append(elem)
    if tail is not None:
        element.tail = tail
    return element, True


def remove_links(element: Element) -> None:
    context: dict[str, Any] = {
        "tag": "text:a",
        "protect_tag": "none",
        "protected": False,
    }
    tree_remove_tag(element, context)


def remove_all_links(document: Document) -> list[tuple[str, int]]:
    """Remove all links and return statistics."""
    body = document.body
    result: list[tuple[str, int]] = []

    result.append(("source, links occurrences:", len(body.get_links())))
    remove_links(body)
    result.append(("final, links occurrences:", len(body.get_links())))

    for line in result:
        print(line[0], line[1])

    return result


def main() -> None:
    document = read_source_document()
    result = remove_all_links(document)
    test_unit(result)
    save_new(document, TARGET)


def test_unit(result: list[tuple[str, int]]) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert result[0][1] == 352
    assert result[1][1] == 0


if __name__ == "__main__":
    main()
