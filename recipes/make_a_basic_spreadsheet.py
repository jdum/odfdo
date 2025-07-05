#!/usr/bin/env python
"""Create a spreadsheet with one table and a few data, strip the table
and compute the table size.
"""

import os
from pathlib import Path

from odfdo import Document, Table

_DOC_SEQUENCE = 460
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_ods"
TARGET = "spreadsheet.ods"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_document():
    # creating an empty spreadsheet document:
    document = Document("spreadsheet")

    # Each sheet of a spreadsheet is a table:
    # setting the beginning width (columns) and height (rows)
    # is not mandatory.
    body = document.body
    body.clear()
    table = Table("First Table", width=20, height=3)
    body.append(table)

    # A table contains rows, we can append some more.
    for _ in range(2):
        table.append_row()
    print("rows in the table (3 at creation + 2 appended):", len(table.rows))

    #  A row contains cells
    for row in table.rows:
        print("row, nb of cells: ", row.y, len(row.cells))

    last_row = table.get_row(-1)
    print("nb of cells of the last row:", len(last_row.cells))

    # cell can have different kind of values
    for row_nb in range(3):
        for col_nb in range(10):
            table.set_value((col_nb, row_nb), f"cell {col_nb} {row_nb}")
    for row_nb in range(3, 5):
        for col_nb in range(10):
            table.set_value((col_nb, row_nb), col_nb * 100 + row_nb)

    # Before saving the document,  we can strip the unused colums:
    print("table size before strip:", table.size)
    table.rstrip()
    print("table size after strip:", table.size)
    print("nb of cells of the last row:", len(table.get_row(-1).cells))
    print("Content of the table (CSV):")
    print(table.to_csv())

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table = document.body.get_table(position=0)
    assert table.size == (10, 5)
    assert table.get_cell("A1").value == "cell 0 0"
    assert table.get_cell("A5").value == 4
    assert table.get_cell("J1").value == "cell 9 0"
    assert table.get_cell("J5").value == 904


if __name__ == "__main__":
    main()
