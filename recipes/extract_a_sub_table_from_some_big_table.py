#!/usr/bin/env python
"""Create a table of 1000 lines and 100 columns, extract a sub table
of 100 lines 26 columns, save the result in a spreadsheet document.
"""
import os
from pathlib import Path

from odfdo import Document, Row, Table

_DOC_SEQUENCE = 450
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "extract_table"
TARGET = "document.ods"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def syracuse(n: int) -> int:
    if n % 2 == 0:
        return n // 2
    return 3 * n + 1


def generate_big_table(table_name) -> Document:
    spreadsheet = Document("spreadsheet")
    body = spreadsheet.body
    body.clear()
    table = Table(table_name)
    body.append(table)

    lines = 1000
    cols = 100

    for line in range(lines):
        row = Row()
        values = []
        n = line
        for _i in range(cols):
            values.append(n)
            n = syracuse(n)
        row.set_values(values)
        table.append(row)

    return spreadsheet


def main():
    table_name = "Big Table"
    spreadsheet = generate_big_table(table_name)
    body = spreadsheet.body
    big_table = body.get_table(name=table_name)
    print("Size of Big Table :", big_table.size)

    # now extract 100 rows of 26 columns :
    table1 = Table("Extract 1")
    for r in range(800, 900):
        row = big_table.get_row(r)
        extracted_values = [row.get_value(x) for x in range(50, 76)]
        new_row = Row()
        new_row.set_values(extracted_values)
        table1.append(new_row)
    body.append(table1)
    print("Size of extracted table 1 :", table1.size)

    # other method
    table2 = Table("Extract 2")
    cells = big_table.get_cells(coord=(50, 800, 75, 899))
    table2.set_cells(coord=(0, 0), cells=cells)
    body.append(table2)
    print("Size of extracted table 2 :", table2.size)

    test_unit(spreadsheet)

    save_new(spreadsheet, TARGET)

    _expected_result = """
Size of Big Table : (100, 1000)
Size of extracted table 1 : (26, 100)
Size of extracted table 2 : (26, 100)
"""


def test_unit(spreadsheet: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    body = spreadsheet.body
    table1 = body.get_table(position=0)
    assert table1.size == (100, 1000)
    table2 = body.get_table(position=1)
    assert table2.size == (26, 100)


if __name__ == "__main__":
    main()
