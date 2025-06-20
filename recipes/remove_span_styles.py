#!/usr/bin/env python
"""Remove span styles (like some words in bold in a paragraph),
except in titles.
"""

import os
import sys
from pathlib import Path

from odfdo import Body, Document, Element

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


def remove_text_span(body: Body) -> None:
    """Remove span styles from an Element, except in titles."""
    tag = "text:span"
    keep_inside_tag = "text:h"
    context = (tag, keep_inside_tag, False)
    body, _is_modified = _tree_remove_tag(body, context)


def _tree_remove_tag(element: Element, context: tuple) -> Element:
    """Send back a copy of the element, without span styles. Element should be
    either paragraph or heading.

    - context: a tuple (tag to remove, protection tag, protection flag)
    where protection tag protects from change any sub elements one level depth
    """
    buffer = element.clone
    modified = False
    sub_elements = []
    tag, keep_inside_tag, protected = context
    if keep_inside_tag and element.tag == keep_inside_tag:
        protect_below = True
    else:
        protect_below = False
    for child in buffer.children:
        striped, is_modified = _tree_remove_tag(
            child, (tag, keep_inside_tag, protect_below)
        )
        if is_modified:
            modified = True
        if isinstance(striped, list):
            for item in striped:
                sub_elements.append(item)
        else:
            sub_elements.append(striped)
    if not protected and element.tag == tag:
        element = []
        modified = True
    else:
        if not modified:
            # no change in element sub tree, no change on element
            return (element, False)
        element.clear()
        try:
            for key, value in buffer.attributes.items():
                element.set_attribute(key, value)
        except ValueError:
            print("Bad attribute in", buffer)
    text = buffer.text
    tail = buffer.tail
    if text is not None:
        element.append(text)
    for child in sub_elements:
        element.append(child)
    if tail is not None:
        if isinstance(element, list):
            element.append(tail)
        else:
            element.tail = tail
    return (element, True)


def clean_document(document: Document) -> None:
    """Remove span styles from a Document."""
    body = document.body

    print("'text:span' occurrences:", len(body.spans))
    remove_text_span(body)
    print("'text:span' occurrences after removal:", len(body.spans))


def main() -> None:
    document = read_source_document()
    clean_document(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(document.body.spans) == 1


if __name__ == "__main__":
    main()
