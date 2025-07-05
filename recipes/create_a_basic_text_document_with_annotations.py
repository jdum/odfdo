#!/usr/bin/env python
"""Create a basic document containing some paragraphs and headers, add some
annotations. Annotations are notes that don't appear in the document but
typically on a side bar in a desktop application. So they are not printed.
"""

import os
from pathlib import Path

from odfdo import Document, Header, Paragraph

_DOC_SEQUENCE = 40
DATA = Path(__file__).parent / "data"
LOREM = (DATA / "lorem.txt").read_text(encoding="utf8")
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_annotations"
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


def make_annotations(document: Document) -> None:
    """Add some annotation on each pragraph of the document."""
    word_position = 0
    for paragraph in document.body.paragraphs:
        # choosing some word of the paragraph to insert the note
        word_position += 3
        some_word = str(paragraph).split()[word_position]

        # Adding Annotation
        paragraph.insert_annotation(
            # The word after what the annotation is inserted:
            after=some_word,
            # The annotation itself, at the end of the page:
            body=f"It's so easy ! (after {some_word!r})",
            # The author of the annotation:
            creator="Bob",
            # A datetime value, by default datetime.now():
            # date= xxx
        )


def main():
    document = make_document()
    make_annotations(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(document.body.get_annotations(creator="Bob")) == 3


if __name__ == "__main__":
    main()
