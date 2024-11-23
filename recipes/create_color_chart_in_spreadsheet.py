#!/usr/bin/env python
"""Create some color chart in a spreadsheet using cells styles.
(adapted from the odfdo library test cases)
"""

from pathlib import Path

from odfdo import (
    Cell,
    Document,
    Row,
    Style,
    Table,
    __version__,
    create_table_cell_style,
    make_table_cell_border_string,
    rgb2hex,
)

_DOC_SEQUENCE = 420
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "chart"
TARGET = "color_chart.ods"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path)


def hello_messages():
    print("odfdo installation test")
    print(f" Version           : {__version__}")
    print()
    print(f"Generating color chart in {TARGET}")
    print("...")


def generate_chart():
    document = Document("spreadsheet")
    body = document.body
    body.clear()
    table = Table("chart")

    for y in range(0, 256, 8):
        row = Row()
        for x in range(0, 256, 32):
            cell_value = (x, y, (x + y) % 256)
            border_rl = make_table_cell_border_string(thick="0.20cm", color="white")
            border_bt = make_table_cell_border_string(
                thick="0.80cm",
                color="white",
            )
            style = create_table_cell_style(
                color="grey",
                background_color=cell_value,
                border_right=border_rl,
                border_left=border_rl,
                border_bottom=border_bt,
                border_top=border_bt,
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


def main():
    hello_messages()
    document = generate_chart()
    save_new(document, TARGET)


if __name__ == "__main__":
    main()
