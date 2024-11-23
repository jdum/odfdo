#!/usr/bin/env python
"""Open a text document with an embedded chart and change some values.
"""

from pathlib import Path

# for cell style
from odfdo import Document

_DOC_SEQUENCE = 295
DATA = Path(__file__).parent / "data"
SOURCE = DATA / "chart.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "modified_chart"
TARGET = "modified_chart.odt"


def save_new(document: Document, name: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main() -> None:
    document = Document(SOURCE)
    change(document)
    save_new(document, TARGET)


def change(document: Document) -> None:
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


if __name__ == "__main__":
    main()
