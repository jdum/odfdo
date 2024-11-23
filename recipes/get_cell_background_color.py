#!/usr/bin/env python
"""Read the background color of a table cell.
"""
import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 440
DATA = Path(__file__).parent / "data"
SOURCE = "cell_color.ods"


def read_source_document():
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def main():
    doc = read_source_document()

    # reading color from the table 0 (first sheet)
    color_b2 = doc.get_cell_background_color(0, "b2")
    print("Color for B2", color_b2)

    color_b3 = doc.get_cell_background_color(0, "b3")
    print("Color for B3", color_b3)

    color_c3 = doc.get_cell_background_color(0, "c3")
    print("Color for C3", color_c3)

    # default is "#ffffff"
    color_d3 = doc.get_cell_background_color(0, "d3")
    print("Color for D3", color_d3)

    # set another default
    color_e3 = doc.get_cell_background_color(0, "e3", "#123456")
    print("Color for e3", color_e3)

    # read very far cell
    color_far = doc.get_cell_background_color(0, (1000, 10000))
    print("Color for far", color_far)

    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    assert color_b2 == "#2a6099"
    assert color_b3 == "#ff4000"
    assert color_c3 == "#ffff00"
    assert color_d3 == "#ffffff"
    assert color_e3 == "#123456"
    assert color_far == "#ffffff"


if __name__ == "__main__":
    main()
