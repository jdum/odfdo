#!/usr/bin/env python
"""Insert an image (e.g. the logo of an event, organization or a Creative Commons
attribution) with size `x,y` at position `x2,y2` on a number of slides in a
presentation slide deck.
"""
from pathlib import Path

# reading image size requires a graphic library
from PIL import Image

from odfdo import Document, Frame

_DOC_SEQUENCE = 250
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "add_logo"
TARGET = "presentation.odp"
DATA = Path(__file__).parent / "data"
SOURCE = DATA / "presentation_wo_logo.odp"
LOGO = DATA / "newlogo.png"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def make_image_size(path, size):
    width, height = Image.open(path).size
    ratio = max(width / size, height / size)
    return (f"{width / ratio:.2f}cm", f"{height / ratio:.2f}cm")


def add_logo(presentation):
    image_position = ("1.50cm", "1.50cm")
    svg_title = "New Logo"
    svg_description = "The new logo with blue background"

    image_size = make_image_size(LOGO, 4.0)
    presentation_body = presentation.body
    uri = presentation.add_file(str(LOGO))

    for slide in presentation_body.get_draw_pages():
        # Create a frame for the image
        image_frame = Frame.image_frame(
            image=uri,
            text="",  # Text over the image object
            size=image_size,  # Display size of image
            anchor_type="page",
            page_number=None,
            position=image_position,
            style=None,
        )
        image_frame.svg_title = svg_title
        image_frame.svg_description = svg_description
        slide.append(image_frame)


def main():
    document = Document(SOURCE)
    add_logo(document)
    save_new(document, TARGET)


if __name__ == "__main__":
    main()
