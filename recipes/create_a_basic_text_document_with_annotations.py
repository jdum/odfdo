#!/usr/bin/env python
"""Create a basic text document with annotations.
"""
import os
from pathlib import Path

from odfdo import Document, Header, Paragraph

_DOC_SEQUENCE = 40
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_annotations"
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
    make_annotations(document)
    test_unit(document)
    save_new(document, TARGET)


def make_annotations(document):
    body = document.body
    title1 = Header(1, "Main title")
    body.append(title1)
    for index in range(3):
        title = Header(2, f"title {index}")
        body.append(title)
        paragraph = Paragraph(LOREM[:240])

        # Adding Annotation
        # Annotations are notes that don't appear in the document but
        # typically on a side bar in a desktop application. So they are not printed.

        # Now we add some annotation on each paragraph
        some_word = str(paragraph).split()[3]
        # choosing the 4th word of the paragraph to insert the note

        paragraph.insert_annotation(
            after=some_word,  # The word after what the annotation is inserted.
            body="It's so easy!",  # The annotation itself, at the end of the page.
            creator="Bob",  # The author of the annotation.
            # date= xxx              A datetime value, by default datetime.now().
        )

        body.append(paragraph)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    assert len(document.body.get_annotations(creator="Bob")) == 3


if __name__ == "__main__":
    main()
