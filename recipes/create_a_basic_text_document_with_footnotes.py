#!/usr/bin/env python
"""Create a basic document containing some paragraphs and headers, add some
footnotes. Footnotes are displayed at the end of the pages of the document.
"""

import os
from pathlib import Path

from odfdo import Document, Header, Paragraph

_DOC_SEQUENCE = 45
DATA = Path(__file__).parent / "data"
LOREM = (DATA / "lorem.txt").read_text(encoding="utf8")
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_footnotes"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def make_document() -> Document:
    """Generate a basic document containing some paragraphs and headers."""
    document = Document("text")
    body = document.body
    body.clear()

    level_1_title = Header(1, "Main title")
    body.append(level_1_title)

    for idx in range(3):
        level_2_title = Header(2, f"title {idx}")
        body.append(level_2_title)
        paragraph = Paragraph(LOREM[:240])
        body.append(paragraph)

    return document


def make_footnotes(document: Document) -> None:
    """Add some footnote for each pragraph of the document."""
    word_position = 0
    note_counter = 0
    for paragraph in document.body.paragraphs:
        # choosing some word of the paragraph to insert the note
        word_position += 3
        some_word = str(paragraph).split()[word_position]

        # Notes are quite complex so they deserve a dedicated API on paragraphs:
        note_counter += 10
        paragraph.insert_note(
            # The word after what the “¹” citation is inserted:
            after=some_word,
            # A unique identifier of the note in the document:
            note_id=f"note{note_counter}",
            # The symbol the user sees to follow the footnote:
            citation="1",
            # The footnote content itself:
            body=('John Doe, A. (2007). "How to cite references", Sample Editions.'),
        )


def main() -> None:
    document = make_document()
    make_footnotes(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(document.body.get_notes()) == 3


if __name__ == "__main__":
    main()
