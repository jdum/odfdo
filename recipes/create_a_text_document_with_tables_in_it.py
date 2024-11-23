#!/usr/bin/env python
"""Build a basic commercial document, with numerical values displayed in
both the text and in a table.
"""

from pathlib import Path

# for cell style
from odfdo import (
    Cell,
    Document,
    Header,
    List,
    ListItem,
    Paragraph,
    Row,
    Table,
    create_table_cell_style,
    make_table_cell_border_string,
)

_DOC_SEQUENCE = 50
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "commercial"
TARGET = "commercial.odt"
TAX_RATE = 0.20


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


class Product:
    def __init__(self, name, price):
        self.name = f"Product {name}"
        self.price = price


def make_product_catalog():
    catalog = []
    price = 10.0
    for prod in range(5):
        catalog.append(Product(chr(65 + prod), price))
        price += 10.5
    return catalog


def main():
    document = generate_commercial()
    save_new(document, TARGET)


def generate_commercial():
    commercial = Document("text")
    body = commercial.body
    catalog = make_product_catalog()

    title1 = Header(1, "Basic commercial document")
    body.append(title1)
    title11 = Header(2, "Available products")
    body.append(title11)
    paragraph = Paragraph("Here the list:")
    body.append(paragraph)

    # List of products in a list :
    product_list = List()  # odfdo.List
    body.append(product_list)
    for product in catalog:
        item = ListItem(f"{product.name:<10}, price: {product.price:.2f} €")
        product_list.append(item)

    title12 = Header(2, "Your command")
    body.append(title12)

    command = {0: 1, 1: 12, 2: 3, 4: 5}

    # A table in the text document :
    table = Table("Table")
    body.append(table)
    row = Row()
    row.set_values(["Product", "Price", "Quantity", "Amount"])
    table.set_row("A1", row)
    # or: table.set_row(0, row)
    row_number = 0
    for item, quantity in command.items():
        prod = catalog[item]
        row = Row()
        row.set_value("A", prod.name)
        # or : row.set_value(0, prod.name)
        cell = Cell()
        cell.set_value(
            prod.price,
            text=f"{prod.price:.2f} €",
            currency="EUR",
            cell_type="float",
        )
        row.set_cell("B", cell)
        # or : row.set_cell(1, cell)
        row.set_value("C", quantity)
        # row.set_value(2, quantity)
        price = prod.price * quantity
        cell = Cell()
        cell.set_value(
            price,
            text=f"{price:.2f} €",
            currency="EUR",
            cell_type="float",
        )
        row.set_cell(3, cell)
        row_number += 1
        table.set_row(row_number, row)

    cols = table.width
    column = cols - 1

    # add merged empty row
    row = Row()
    row_number += 1
    table.set_row(row_number, row)
    table.set_span((0, row_number, 3, row_number))

    # make total
    row = Row()
    row.set_value(column - 1, "Total:")
    total = sum(table.get_column_values(column)[1:-1])
    cell = Cell()
    cell.set_value(
        total,
        text=f"{total:.2f} €",
        currency="EUR",
        cell_type="float",
    )
    row.set_cell(column, cell)
    row_number += 1
    table.set_row(row_number, row)

    # let merge some cells
    table.set_span((column - 3, row_number, column - 1, row_number), merge=True)

    row = Row()
    row.set_value(column - 1, "Total with tax:")
    total *= 1 + TAX_RATE
    cell = Cell()
    cell.set_value(
        total,
        text=f"{total:.2f} €",
        currency="EUR",
        cell_type="float",
    )
    row.set_cell(column, cell)
    row_number += 1
    table.set_row(row_number, row)
    # let merge some cells
    table.set_span((column - 3, row_number, column - 1, row_number), merge=True)

    # Let's add some style on first row
    border = make_table_cell_border_string(thick="0.03cm", color="black")
    cell_style = create_table_cell_style(
        color="black",
        background_color=(210, 210, 210),
        border_right=border,
        border_left=border,
        border_bottom=border,
        border_top=border,
    )
    style_name = commercial.insert_style(style=cell_style, automatic=True)

    row = table.get_row(0)
    # for cell in row.get_cells(): #possible, but .traverse() is better
    for cell in row.traverse():
        cell.style = style_name
        row.set_cell(x=cell.x, cell=cell)
    table.set_row(row.y, row)

    return commercial


if __name__ == "__main__":
    main()
