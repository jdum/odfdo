#!/usr/bin/env python
"""Read the background color of a table cell."""

import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 440
DATA = Path(__file__).parent / "data"
SOURCE = "cell_color.ods"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def read_color(document: Document) -> list[tuple[str, str]]:
    """Read cell background color from the table 0 (first sheet)."""
    result = []

    color = document.get_cell_background_color(0, "b2")
    result.append(("Color for B2", color))

    color = document.get_cell_background_color(0, "b3")
    result.append(("Color for B3", color))

    color = document.get_cell_background_color(0, "c3")
    result.append(("Color for C3", color))

    color = document.get_cell_background_color(0, "d3")
    result.append(('Color for D3 (default is "#ffffff")', color))

    color = document.get_cell_background_color(0, "e3", "#123456")
    result.append(("Color for e3 (providing another default)", color))

    color = document.get_cell_background_color(0, (1000, 10000))
    result.append(("Color for far away cell", color))

    print("\n".join(": ".join(x) for x in result))
    return result


def main() -> None:
    document = read_source_document()
    result = read_color(document)
    test_unit(result)


def test_unit(colors: list[tuple[str, str]]) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert colors[0][1] == "#2a6099"
    assert colors[1][1] == "#ff4000"
    assert colors[2][1] == "#ffff00"
    assert colors[3][1] == "#ffffff"
    assert colors[4][1] == "#123456"
    assert colors[5][1] == "#ffffff"


if __name__ == "__main__":
    main()
