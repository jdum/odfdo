#!/usr/bin/env python
"""Remove all links from a document, transforming each link information (URL,
text) into a footnote. Of course, removing links already inside notes, just
keeping plain text URL. (Side note: most office suite dislike notes in notes)
"""

import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 500
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "footnote1"
TARGET = "document.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def remove_links(element):
    tag = "text:a"
    keep_inside_tag = "None"
    context = (tag, keep_inside_tag, False)
    element, _is_modified = _tree_remove_tag(element, context)


def main():
    try:
        source = Path(sys.argv[1])
    except IndexError:
        source = DATA / SOURCE

    document = Document(str(source))
    body = document.body

    print("Moving links to footnotes from", source)
    print("links occurrences:", len(body.get_links()))
    print("footnotes occurences:", len(body.get_notes()))

    counter_links_in_notes = 0
    for note in body.get_notes():
        for link in note.get_links():
            counter_links_in_notes += 1
            url = link.get_attribute("xlink:href")
            tail = link.tail
            new_tail = f" (link: {url}) {tail}"
            link.tail = new_tail
            remove_links(note)

    print("links in notes:", counter_links_in_notes)

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

    print("links occurrences:", len(body.get_links()))
    print("footnotes occurences:", len(body.get_notes()))

    save_new(document, TARGET)


def _tree_remove_tag(element, context):
    """Remove tag in the element, recursive.
    - context: tuple (tag to remove, protection tag, protection flag)
    where protection tag protect from change sub elements one sub
    level depth"""
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
            print("Incorrect attribute in", buffer)
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
