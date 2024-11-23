#!/usr/bin/env python
"""Create an empty text document and add a picture in a frame.
"""
from pathlib import Path

from odfdo import Document, Frame, Paragraph

_DOC_SEQUENCE = 65
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_picture"
TARGET = "document.odt"
DATA = Path(__file__).parent / "data"
IMAGE = DATA / "newlogo.png"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = Document("text")
    body = document.body
    image_path = str(DATA / IMAGE)
    uri = document.add_file(image_path)
    image_frame = Frame.image_frame(
        uri,
        size=("6cm", "4cm"),
        position=("5cm", "10cm"),
    )

    # put image frame in a paragraph:
    paragraph = Paragraph("")
    paragraph.append(image_frame)
    body.append(paragraph)

    save_new(document, TARGET)


if __name__ == "__main__":
    main()
