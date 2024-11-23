#!/usr/bin/env python
"""Write a basic "Hello World" in the middle of the first page of a presentaion.
"""
from pathlib import Path

from odfdo import Document, DrawPage, Frame

_DOC_SEQUENCE = 7
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_odp"
TARGET = "hello.odp"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = Document("presentation")
    body = document.body
    body.clear()

    page = DrawPage("page1", name="Page 1")
    text_frame = Frame.text_frame(
        "Hello World",
        size=("7cm", "5cm"),
        position=("11cm", "8cm"),
        style="Standard",
        text_style="Standard",
    )
    page.append(text_frame)
    body.append(page)

    save_new(document, TARGET)


if __name__ == "__main__":
    main()
