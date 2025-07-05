#!/usr/bin/env python
"""Open a table of 1000 lines and 100 columns, extract a sub table
of 100 lines 26 columns, save the result in a spreadsheet document.
"""

import os
import sys
from pathlib import Path

from odfdo import Document, Row, Table

_DOC_SEQUENCE = 450
DATA = Path(__file__).parent / "data"
SOURCE = "big_table.ods"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "extract_table"
TARGET = "document.ods"


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


def extract_sub_tables(document: Document) -> Document:
    """Return a spreadsheet with 2 sheets extracted from the imput document."""
    # Expected_result:
    #  Size of Big Table : (100, 1000)
    #  Size of extracted table 1 : (26, 100)
    #  Size of extracted table 2 : (26, 100)
    #
    big_table = document.body.get_table(name="Big Table")
    print("Size of Big Table :", big_table.size)

    extracted = Document("ods")
    extracted.body.clear()
    # now extract 100 rows of 26 columns :
    table1 = Table("Extract 1")
    for r in range(800, 900):
        row = big_table.get_row(r)
        extracted_values = [row.get_value(x) for x in range(50, 76)]
        new_row = Row()
        new_row.set_values(extracted_values)
        table1.append(new_row)
    extracted.body.append(table1)
    print("Size of extracted table 1 :", table1.size)

    # other method
    table2 = Table("Extract 2")
    cells = big_table.get_cells(coord=(50, 800, 75, 899))
    table2.set_cells(coord=(0, 0), cells=cells)
    extracted.body.append(table2)
    print("Size of extracted table 2 :", table2.size)

    return extracted


def main() -> None:
    document = read_source_document()
    extracted = extract_sub_tables(document)
    test_unit(extracted)
    save_new(extracted, TARGET)


def test_unit(spreadsheet: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    body = spreadsheet.body
    table1 = body.get_table(position=0)
    assert table1.size == (26, 100)
    table2 = body.get_table(position=1)
    assert table2.size == (26, 100)


if __name__ == "__main__":
    main()
