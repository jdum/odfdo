#!/usr/bin/env python
"""Create some color chart in a spreadsheet using cells styles functions.

For cells, use of functions:
    make_table_cell_border_string()
    create_table_cell_style()
    rgb2hex()

Apply a row style to define the row height.

Apply a column style to define the column width.
"""

import os
from pathlib import Path

from odfdo import (
    Cell,
    Document,
    Row,
    Style,
    Table,
    create_table_cell_style,
    make_table_cell_border_string,
    rgb2hex,
)

_DOC_SEQUENCE = 420
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "chart"
TARGET = "color_chart.ods"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_chart() -> Document:
    """Generate a spreadsheet with colored cells.

    For cells, use of functions:
        make_table_cell_border_string()
        create_table_cell_style()
        rgb2hex()

    Apply a row style to define the row height.

    Apply a column style to define the column width.
    """
    document = Document("spreadsheet")
    body = document.body
    body.clear()
    table = Table("chart")

    for y in range(0, 256, 8):
        row = Row()
        for x in range(0, 256, 32):
            cell_value = (x, y, (x + y) % 256)
            border_right_left = make_table_cell_border_string(
                thick="0.20cm",
                color="white",
            )
            border_top_bottom = make_table_cell_border_string(
                thick="0.80cm",
                color="white",
            )
            style = create_table_cell_style(
                color="grey",
                background_color=cell_value,
                border_right=border_right_left,
                border_left=border_right_left,
                border_bottom=border_top_bottom,
                border_top=border_top_bottom,
            )
            name = document.insert_style(style=style, automatic=True)
            cell = Cell(value=rgb2hex(cell_value), style=name)
            row.append_cell(cell)
        table.append_row(row)

        row_style = Style("table-row", height="1.80cm")
        name_style_row = document.insert_style(style=row_style, automatic=True)
        for row in table.rows:
            row.style = name_style_row
            table.set_row(row.y, row)

        col_style = Style("table-column", width="3.6cm")
        name = document.insert_style(style=col_style, automatic=True)
        for column in table.columns:
            column.style = col_style
            table.set_column(column.x, column)

    body.append(table)

    return document


def main() -> None:
    document = generate_chart()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table = document.body.get_table(name="chart")
    assert isinstance(table, Table)

    cell = table.get_cell("A1")
    assert cell.value == "#000000"
    style = document.get_style("table-cell", cell.style)
    assert style.get_properties()["fo:background-color"] == cell.value

    cell = table.get_cell("H1")
    assert cell.value == "#E000E0"
    style = document.get_style("table-cell", cell.style)
    assert style.get_properties()["fo:background-color"] == cell.value

    cell = table.get_cell("A32")
    assert cell.value == "#00F8F8"
    style = document.get_style("table-cell", cell.style)
    assert style.get_properties()["fo:background-color"] == cell.value

    cell = table.get_cell("H32")
    assert cell.value == "#E0F8D8"
    style = document.get_style("table-cell", cell.style)
    assert style.get_properties()["fo:background-color"] == cell.value


if __name__ == "__main__":
    main()
