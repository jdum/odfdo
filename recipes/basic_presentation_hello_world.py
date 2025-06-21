#!/usr/bin/env python
"""Write a basic "Hello World" in the middle of the first page
of a presentation.
"""

import os
from pathlib import Path

from odfdo import Document, DrawPage, Frame

_DOC_SEQUENCE = 7
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_odp"
TARGET = "hello.odp"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def add_text_frame(document: Document, text: str) -> None:
    """Add a text frame to an empty presentation."""
    body = document.body
    body.clear()

    page = DrawPage("page1", name="Page 1")
    text_frame = Frame.text_frame(
        text,
        size=("7cm", "5cm"),
        position=("11cm", "8cm"),
        style="Standard",
        text_style="Standard",
    )
    page.append(text_frame)
    body.append(page)


def main() -> None:
    document = Document("presentation")
    add_text_frame(document, "Hello world!")
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    frames = document.body.get_frames()
    assert len(frames) == 1
    assert str(frames[0]).strip() == "Hello world!"


if __name__ == "__main__":
    main()
