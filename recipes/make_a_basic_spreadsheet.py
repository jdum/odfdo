#!/usr/bin/env python
"""Create a spreadsheet with one table and a few data, strip the table
and compute the table size.
"""
from pathlib import Path

from odfdo import Document, Table

_DOC_SEQUENCE = 460
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_ods"
TARGET = "spreadsheet.ods"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = generate_document()
    save_new(document, TARGET)


def generate_document():
    # creating an empty spreadsheet document:
    document = Document("spreadsheet")

    # Each sheet of a spreadsheet is a table:
    # setting drom the beginning width (columns) and height (rows)
    # is not mandatory, but a good practice, since odfdo don't check
    # actual existence of cells
    body = document.body
    body.clear()
    table = Table("First Table", width=20, height=3)
    body.append(table)

    # A table contains rows, we can append some more.
    for _ in range(2):
        table.append_row()
    print("rows in the table (3+2):", len(table.rows))

    #  A row contains cells
    for row in table.rows:
        print("row, nb of cells ", row.y, len(row.cells))

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
    print("table size:", table.size)
    table.rstrip()
    print("table size after strip:", table.size)
    print("nb of cells of the last row:", len(table.get_row(-1).cells))
    print("Content of the table:")
    print(table.to_csv())

    return document


if __name__ == "__main__":
    main()
