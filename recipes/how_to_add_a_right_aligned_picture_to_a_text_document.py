#!/usr/bin/env python
"""Create an empty text document and add a picture in a frame,
aligned to the right or to the left.

Aligning an image requires applying a style to the frame. To do
this, use the default frame position style and customize it. The
frame position style allows you to choose alignment relative to
the paragraph (default) or the page.
"""

import os
from pathlib import Path

from odfdo import Document, Frame, Paragraph, default_frame_position_style

_DOC_SEQUENCE = 66
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_picture_right"
TARGET = "document.odt"
DATA = Path(__file__).parent / "data"
IMAGE = DATA / "newlogo.png"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def make_document() -> Document:
    """Generate a document containing two instances of an image,
    align one left, the other right.
    """
    document = Document("text")

    # add an image to the document, remember its URI
    image_path = str(DATA / IMAGE)
    uri = document.add_file(image_path)

    # add a frame style to the document, right alignment
    right_style = default_frame_position_style(
        name="right_frame", horizontal_pos="right"
    )
    document.insert_style(right_style)

    # add a frame style to the document, left alignment
    left_style = default_frame_position_style(
        name="left_frame", horizontal_pos="left", horizontal_rel="page"
    )
    document.insert_style(left_style)

    # make the image frames using previous informations
    image_frame_right = Frame.image_frame(
        uri,
        size=("6cm", "4cm"),
        position=("0cm", "5cm"),
        style=right_style.name,
    )
    image_frame_left = Frame.image_frame(
        uri,
        size=("9cm", "6cm"),
        position=("0cm", "12cm"),
        style=left_style.name,
    )

    # put image frame in a paragraph:
    paragraph = Paragraph("")
    paragraph.append(image_frame_right)
    paragraph.append(image_frame_left)
    document.body.append(paragraph)

    return document


def main() -> None:
    document = make_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len([s for s in document.get_styles() if s.family == "graphic"]) >= 2
    graphic_style_names = [s.name for s in document.get_styles("graphic")]
    assert "right_frame" in graphic_style_names
    assert "left_frame" in graphic_style_names


if __name__ == "__main__":
    main()
