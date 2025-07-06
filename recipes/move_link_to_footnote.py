#!/usr/bin/env python
"""Remove all links from a document, transforming each link information (URL,
text) into a footnote. Of course, removing links already inside notes, just
keeping plain text URL. (Side note: most office suite dislike notes in notes)
"""

import os
import sys
from pathlib import Path

from odfdo import Document, Link, remove_tree

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
        remove_tree(note, Link)
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
        remove_tree(paragraph, Link)

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
