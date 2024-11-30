#!/usr/bin/env python
"""Transform a not styled document into a multi styled document,
by changing size and color of each parts of words.
"""
import os
from itertools import chain
from pathlib import Path

from odfdo import Document, Style

_DOC_SEQUENCE = 300
DATA = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "styled3"
TARGET = "dormeur_styled.odt"
SOURCE = DATA / "dormeur_notstyled.odt"
RANDOM_SEED = 1234


class SimpleRandom:
    """Q&D reproductible random generator for tests."""

    MODULUS = 2**31 - 1
    MAXI = 2**31 - 2

    def __init__(self):
        self.current = 16807

    def _next_number(self):
        self.current = (16807 * self.current) % self.MODULUS

    def set_seed(self, seed=16807):
        self.current = seed

    def randint(self, max_value):
        self._next_number()
        return int(self.current * max_value / self.MAXI + 1)


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def color_hex(r, g, b):
    return f"#{r:02X}{g:02X}{b:02X}"


def style_name_index(index):
    return f"rnd_{index}"


def generate_random_styles(document, rnd):
    """Generate 64 random styles."""
    for index in range(1, 64):
        style = Style(
            "text",
            name=style_name_index(index),
            color=color_hex(rnd.randint(256), rnd.randint(256), rnd.randint(256)),
            size=f"{8 + index / 5}",
        )
        document.insert_style(style)


def main():
    document = Document(SOURCE)
    add_styles(document)
    save_new(document, TARGET)


def add_styles(document):
    rnd = SimpleRandom()
    body = document.body

    generate_random_styles(document, rnd)

    words = sorted(set(str(body).split()))
    for word in words:
        style_name = style_name_index(rnd.randint(64))
        for paragraph in chain(body.paragraphs, body.headers):
            # apply style to each text matching with the regex of some word
            paragraph.set_span(style_name, regex=word)

    # only for test suite:
    if "ODFDO_TESTING" in os.environ:
        print(len(body.spans))
        assert len(body.spans) == 157


if __name__ == "__main__":
    main()
