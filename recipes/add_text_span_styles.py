#!/usr/bin/env python
"""Transform a not styled document into a multi styled document,
by changing size and color of each parts of words.
"""
from pathlib import Path
from random import randrange

from odfdo import Document, Style

DATA = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "styled3"
TARGET = "dormeur_styled.odt"
SOURCE = DATA / "dormeur_notstyled.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def color_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"


def random_style_name():
    """Returns a random style name."""
    return f"rnd_{randrange(64)}"


def generate_random_styles(document):
    """Generate 64 random styles."""
    for index in range(64):
        style = Style(
            "text",
            name=f"rnd_{index}",
            color=color_hex(randrange(256), randrange(256), randrange(256)),
            size=f"{8 + index / 5}",
        )
        document.insert_style(style)


def main():
    document = Document(SOURCE)
    add_styles(document)
    save_new(document, TARGET)


def add_styles(document):
    body = document.body

    generate_random_styles(document)

    words = set(body.text_recursive.split())
    for word in words:
        style_name = random_style_name()
        for paragraph in body.get_paragraphs() + body.get_headers():
            # apply style to each text matching with the regex of some word
            paragraph.set_span(style_name, regex=word)


if __name__ == "__main__":
    main()
