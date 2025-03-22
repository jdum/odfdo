#!/usr/bin/env python
"""Remove the links (the text:a tag), keeping the inner text."""

import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 510
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "nolink"
TARGET = "document.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    try:
        source = Path(sys.argv[1])
    except IndexError:
        source = DATA / SOURCE

    document = Document(str(source))
    body = document.body

    print("Removing links from", source)
    print("'text:a' occurrences:", len(body.get_links()))

    remove_links(body)
    print("'text:a' occurrences after removal:", len(body.get_links()))

    save_new(document, TARGET)


def remove_links(element):
    tag = "text:a"
    keep_inside_tag = "None"
    context = (tag, keep_inside_tag, False)
    element, _is_modified = _tree_remove_tag(element, context)


def _tree_remove_tag(element, context):
    """Remove tag in the element, recursive.

    - context: a tuple (tag to remove, protection tag, protection flag)
    where protection tag protect from change sub elements one sub level depth
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


if __name__ == "__main__":
    main()
