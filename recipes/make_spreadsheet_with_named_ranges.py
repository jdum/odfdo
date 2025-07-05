#!/usr/bin/env python
"""Create a spreadsheet with two tables, using named ranges to fill cells."""

import os
from pathlib import Path

from odfdo import Document, Table

_DOC_SEQUENCE = 470
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "named_range"
TARGET = "spreadsheet.ods"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def make_some_table_content() -> Table:
    table = Table("First Table")
    # populate the table :
    for index in range(10):
        table.set_value((1, index), (index + 1) ** 2)
    table.set_value("A11", "Total:")
    return table


def generate_document() -> Document:
    document = Document("spreadsheet")
    body = document.body
    body.clear()

    table = make_some_table_content()
    body.append(table)

    # lets define a named range for the 10 values :
    range_squares = "B1:B10"
    name = "squares_values"
    table_name = table.name
    table.set_named_range(name, range_squares, table_name)

    # we can define a single cell range, using notation "B11" or (1, 10) :
    table.set_named_range("total", (1, 10), table_name)

    # get named range values :
    values = table.get_named_range("squares_values").get_values(flat=True)

    # set named range value :
    result = sum(values)
    table.get_named_range("total").set_value(result)

    # lets use the named ranges from a second table :
    table2 = Table("Second Table")
    body.append(table2)

    named_range1 = table2.get_named_range("total")
    table2.set_value("A1", "name:")
    table2.set_value("B1", named_range1.name)
    table2.set_value("A2", "range:")
    table2.set_value("B2", str(named_range1.crange))
    table2.set_value("A3", "from table:")
    table2.set_value("B3", named_range1.table_name)
    table2.set_value("A4", "content:")
    table2.set_value("B4", named_range1.get_value())

    named_range2 = table2.get_named_range("squares_values")
    table2.set_value("D1", "name:")
    table2.set_value("E1", named_range2.name)
    table2.set_value("D2", "range:")
    table2.set_value("E2", str(named_range2.crange))
    table2.set_value("D3", "from table:")
    table2.set_value("E3", named_range2.table_name)
    table2.set_value("D4", "content:")
    # using "E4:4" notaion is a little hack for the area starting at E4 on row 4
    table2.set_values(values=[named_range2.get_values(flat=True)], coord="E4:4")

    print("Content of the table 1:")
    print(table.name)
    print(table.to_csv())
    print("Content of the table 2:")
    print(table2.name)
    print(table2.to_csv())

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table1 = document.body.get_table(0)
    assert table1.get_cell("B1").value == 1
    assert table1.get_cell("B10").value == 100
    assert table1.get_cell("B11").value == 385
    table2 = document.body.get_table(1)
    assert table2.get_cell("B4").value == 385
    assert table2.get_cell("N4").value == 100


if __name__ == "__main__":
    main()
