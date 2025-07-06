#!/usr/bin/env python
"""Transpose a table. Create a spreadsheet table (for example: 50 rows and
20 columns), then create a new table in a separate sheet where the columns
and rows are swapped (for example: 20 rows and 50 columns).
"""

import os
from pathlib import Path

from odfdo import Document, Row, Table

_DOC_SEQUENCE = 800
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "transpose"
TARGET = "transposed.ods"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_document() -> Document:
    """Return a spreadshhet with table swapped by 2 different methods."""
    spreadsheet = Document("spreadsheet")

    # Populate the table in the spreadsheet
    body = spreadsheet.body
    body.clear()
    table = Table("Table")
    body.append(table)

    lines = 50
    cols = 20

    for line in range(lines):
        row = Row()
        for column in range(cols):
            row.set_value(column, f"{chr(65 + column)}{line + 1}")
        table.append(row)

    print(f"Size of Table : {table.size}")

    table2 = Table("Symmetry")

    # building the symetric table using classical method :
    for x in range(cols):
        values = table.get_column_values(x)
        table2.set_row_values(x, values)
    body.append(table2)

    print(f"Symmetrical table size 2 : {table2.size}")

    # a more simple solution with the table.transpose() method :
    table3 = table.clone
    table3.transpose()
    table3.name = "Transpose"
    body.append(table3)

    print(f"Symmetrical table size 3 : {table3.size}")
    return spreadsheet


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table0 = document.body.get_table(position=0)
    table1 = document.body.get_table(position=1)
    table2 = document.body.get_table(position=2)
    assert table0.size == (20, 50)
    assert table1.size == (50, 20)
    assert table2.size == (50, 20)


if __name__ == "__main__":
    main()
