#!/usr/bin/env python
"""Create a basic text document with footnotes.
"""
import os
from pathlib import Path

from odfdo import Document, Header, Paragraph

_DOC_SEQUENCE = 45
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_footnotes"
DATA = Path(__file__).parent / "data"
LOREM = (DATA / "lorem.txt").read_text(encoding="utf8")
TARGET = "document.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = Document("text")
    make_footnotes(document)
    test_unit(document)
    save_new(document, TARGET)


def make_footnotes(document):
    body = document.body

    # Add content (See Create_a_basic_document.py)
    title1 = Header(1, "Main title")
    body.append(title1)
    for index in range(3):
        title = Header(2, f"title {index}")
        body.append(title)
        paragraph = Paragraph(LOREM[:240])

        # Adding Footnote
        # Now we add a footnote on each paragraph
        # Notes are quite complex so they deserve a dedicated API on paragraphs:
        some_word = str(paragraph).split()[3]
        # choosing the 4th word of the paragraph to insert the note
        paragraph.insert_note(
            after=some_word,  # The word after what the “¹” citation is inserted.
            note_id=f"note{index}",  # The unique identifier of the note in the document.
            citation="1",  # The symbol the user sees to follow the footnote.
            body=(
                f'Author{index}, A. (2007). "How to cite references", Sample Editions.'
                # The footnote itself, at the end of the page.
            ),
        )

        body.append(paragraph)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    assert len(document.body.get_notes()) == 3


if __name__ == "__main__":
    main()
