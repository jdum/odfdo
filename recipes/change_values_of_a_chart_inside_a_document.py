#!/usr/bin/env python
"""Open a text document with an embedded chart and change some values."""

import os
import sys
from pathlib import Path

# for cell style
from odfdo import Document

_DOC_SEQUENCE = 295
DATA = Path(__file__).parent / "data"
SOURCE = "chart.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "modified_chart"
TARGET = "modified_chart.odt"


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


def change(document: Document) -> None:
    """Change some values in the embedded chart table."""
    # list the parts if needed
    print(document.parts)
    # -> ['mimetype', 'ObjectReplacements/Object 1', 'Object 1/meta.xml', 'Object 1/styles.xml', 'Object 1/content.xml', ...

    part = document.get_part("Object 1/content.xml")
    body = part.body
    table = body.get_table(0)

    # if needed, get the values:
    values = table.get_values()
    print(values)
    # -> [
    #     [None, "", "Column 2", "Column 3"],
    #     ["Row 1", Decimal("NaN"), 10, 20],
    #     ["Row 2", Decimal("NaN"), 30, 40],
    #     ["Row 3", Decimal("NaN"), 50, 360],
    #     ["Row 4", Decimal("NaN"), Decimal("9.02"), Decimal("6.2")],
    # ]

    # change some values
    table.set_value("A2", "label changed")
    table.set_value("D3", 4000)
    table.set_value("D4", 4321)


def main() -> None:
    document = read_source_document()
    change(document)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    part = document.get_part("Object 1/content.xml")
    table = part.body.get_table(0)
    assert table.get_value("A3") == "Row 2"
    assert table.get_value("A2") == "label changed"
    assert table.get_value("D3") == 4000
    assert table.get_value("D4") == 4321


if __name__ == "__main__":
    main()
