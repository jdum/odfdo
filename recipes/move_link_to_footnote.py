#!/usr/bin/env python
"""Remove all links from a document, transforming each link information (URL,
text) into a footnote. Of course, removing links already inside notes, just
keeping plain text URL. (Side note: most office suite dislike notes in notes)
"""

import os
import sys
from pathlib import Path
from typing import Any

from odfdo import Document, Element

_DOC_SEQUENCE = 500
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "footnote1"
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


def convert_links(document: Document) -> list[tuple[str, int]]:
    body = document.body
    result: list[tuple[str, int]] = []

    result.append(("source, links occurrences:", len(body.get_links())))
    result.append(("source, footnotes occurences:", len(body.get_notes())))

    counter_links_in_notes = 0
    for note in body.get_notes():
        for link in note.get_links():
            counter_links_in_notes += 1
            url = link.get_attribute("xlink:href")
            tail = link.tail
            new_tail = f" (link: {url}) {tail}"
            link.tail = new_tail
            remove_links(note)
    result.append(("source, links inside notes:", counter_links_in_notes))

    counter_added_note = 0  # added notes counter
    for paragraph in body.paragraphs:
        for link in paragraph.get_links():
            url = link.get_attribute("xlink:href")
            text = link.inner_text
            counter_added_note += 1
            paragraph.insert_note(
                after=link,  # citation is inserted after current link
                note_id=f"my_note_{counter_added_note}",
                citation="1",  # The symbol the user sees to follow the footnote.
                # The footnote itself, at the end of the page:
                body=(f". {text}, link: {url}"),
            )
        remove_links(paragraph)

    result.append(("final, links occurrences:", len(body.get_links())))
    result.append(("final, added footnotes:", counter_added_note))
    result.append(("final, footnotes occurences:", len(body.get_notes())))

    for line in result:
        print(line[0], line[1])

    return result


def main() -> None:
    document = read_source_document()
    result = convert_links(document)
    test_unit(result)
    save_new(document, TARGET)


def test_unit(result: list[tuple[str, int]]) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert result[0][1] == 352
    assert result[1][1] == 49
    assert result[2][1] == 38
    assert result[3][1] == 0
    assert result[4][1] == 314
    assert result[5][1] == 363


if __name__ == "__main__":
    main()
