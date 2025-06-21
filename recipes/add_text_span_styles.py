#!/usr/bin/env python
"""Transform a not styled document into a multi styled document,
by changing size and color of each parts of words.
"""

import os
import sys
from itertools import chain
from pathlib import Path

from odfdo import Document, Style

_DOC_SEQUENCE = 300
DATA = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "styled3"
SOURCE = "dormeur_notstyled.odt"
TARGET = "dormeur_styled.odt"
RANDOM_SEED = 1234


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


class SimpleRandom:
    """Q&D reproductible random generator for tests."""

    MODULUS = 2**31 - 1
    MAXI = 2**31 - 2

    def __init__(self) -> None:
        self.current = 16807

    def _next_number(self) -> None:
        self.current = (16807 * self.current) % self.MODULUS

    def set_seed(self, seed: int = 16807) -> None:
        self.current = seed

    def randint(self, max_value: int) -> int:
        self._next_number()
        return int(self.current * max_value / self.MAXI + 1)


def color_hex(r: int, g: int, b: int) -> str:
    """Convert red, green, blue values to #rgb string."""
    return f"#{r:02X}{g:02X}{b:02X}"


def style_name_index(index: int) -> str:
    """Generate a style_name."""
    return f"rnd_{index}"


def generate_random_styles(document: Document, rnd: SimpleRandom) -> None:
    """Generate 64 random styles."""
    for index in range(1, 64):
        style = Style(
            "text",
            name=style_name_index(index),
            color=color_hex(rnd.randint(256), rnd.randint(256), rnd.randint(256)),
            size=f"{8 + index / 5}",
        )
        document.insert_style(style)


def add_styles(document: Document) -> None:
    """Change randomly size and color of words."""
    rnd = SimpleRandom()
    body = document.body

    generate_random_styles(document, rnd)

    words = sorted(set(str(body).split()))
    for word in words:
        style_name = style_name_index(rnd.randint(64))
        for paragraph in chain(body.paragraphs, body.headers):
            # apply style to each text matching with the regex of some word
            paragraph.set_span(style_name, regex=word)


def main():
    document = read_source_document()
    add_styles(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(document.body.spans) == 157


if __name__ == "__main__":
    main()
