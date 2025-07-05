#!/usr/bin/env python
"""Insert a circle and a lot of lines (a fractal) in a text document."""

from __future__ import annotations

import cmath
import os
from pathlib import Path

from odfdo import Document, EllipseShape, Header, LineShape, Paragraph

_DOC_SEQUENCE = 100
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_drawing"
TARGET = "koch.odt"

CYCLES = 4  # beware, 5 is big, 6 is too big to display...


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def cm(x: float) -> str:
    """Return the value as cm string."""
    return f"{x:.2f}cm"


class Vector:
    """Vector class with Koch calculation."""

    def __init__(self, a: float | complex, b: float | complex) -> None:
        self.a = a
        self.b = b

    def koch_split(self) -> list[Vector]:
        c = self.a + 1.0 / 3.0 * (self.b - self.a)
        d = self.a + 2.0 / 3.0 * (self.b - self.a)
        m = 0.5 * (self.a + self.b)
        e = m + (d - c) * complex(0, -1)
        return [Vector(self.a, c), Vector(c, e), Vector(e, d), Vector(d, self.b)]

    def centimeter(self, index: int) -> tuple[str, str]:
        if index == 0:
            m = self.a
        else:
            m = self.b
        return (cm(m.real), cm(m.imag))


def koch(vector_list: list[Vector], cycles: int = 2) -> list[Vector]:
    """Generate a Koch fractal."""
    if cycles <= 0:
        return vector_list
    else:
        new_vector_list: list[Vector] = []
        for vector in vector_list:
            new_vector_list.extend(vector.koch_split())
        return koch(new_vector_list, cycles - 1)


def make_fractal_coords(
    side: float,
    vert_position: float,
) -> tuple[float | complex, list[Vector]]:
    """Return center and coordinates of a Koch fractal image."""
    orig = complex((17 - side) / 2.0, vert_position)
    v1 = Vector(orig, orig + complex(side, 0))
    v2 = Vector(v1.b, orig + cmath.rect(side, cmath.pi / 3))
    v3 = Vector(v2.b, orig)
    center: float | complex = (v1.a + v1.b + v2.b) / 3
    vector_list = koch([v1, v2, v3], cycles=CYCLES)
    return center, vector_list


def generate_document() -> Document:
    """Generate a document with image in it."""
    document = Document("text")
    body = document.body

    print("Making some Koch fractal")
    title = Header(1, "Some Koch fractal")
    body.append(title)

    style = document.get_style("graphic")
    style.set_properties({"svg:stroke_color": "#0000ff"})
    style.set_properties(fill_color="#ffffcc")

    paragraph = Paragraph("")
    body.append(paragraph)

    # some computation of oordinates
    center, vector_list = make_fractal_coords(side=12.0, vert_position=8.0)

    # create a circle
    radius = 8.0
    pos = center - complex(radius, radius)
    circle = EllipseShape(
        size=(cm(radius * 2), cm(radius * 2)),
        position=(cm(pos.real), cm(pos.imag)),
    )
    paragraph.append(circle)

    # create a drawing with a lot of lines
    paragraph.append(f"number of lines: {len(vector_list)}")
    for vector in vector_list:
        line = LineShape(p1=vector.centimeter(0), p2=vector.centimeter(1))
        paragraph.append(line)

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(document.body.paragraphs) == 2
    assert len(document.body.get_draw_lines()) == 768


if __name__ == "__main__":
    main()
