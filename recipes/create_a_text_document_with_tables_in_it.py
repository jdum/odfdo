#!/usr/bin/env python
"""
Build a basic commercial document, with numerical values displayed in both the
text and in a table.
"""

import os

from odfdo import Document, Header, Paragraph, List, ListItem, Style
from odfdo import Table, Row, Cell

# for cell style
from odfdo import create_table_cell_style, make_table_cell_border_string

# basic commercial document v1


class Product:
    def __init__(self, name, price):
        self.name = "Product %s" % name
        self.price = price


def make_catalog():
    cat_list = []
    price = 10.0
    for p in range(5):
        cat_list.append(Product(chr(65 + p), price))
        price += 10.5
    return cat_list


tax_rate = 0.196

if __name__ == "__main__":
    commercial = Document("text")
    body = commercial.body
    catalog = make_catalog()

    title1 = Header(1, "Basic commercial document")
    body.append(title1)
    title11 = Header(2, "Available products")
    body.append(title11)
    paragraph = Paragraph("Here the list:")
    body.append(paragraph)

    # List of products in a list :
    product_list = List()
    body.append(product_list)
    for product in catalog:
        item = ListItem("%-10s, price: %.2f €" % (product.name, product.price))
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
            prod.price, text="%.2f €" % prod.price, currency="EUR", cell_type="float"
        )
        row.set_cell("B", cell)
        # or : row.set_cell(1, cell)
        row.set_value("C", quantity)
        # row.set_value(2, quantity)
        p = prod.price * quantity
        cell = Cell()
        cell.set_value(p, text="%.2f €" % p, currency="EUR", cell_type="float")
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
    cell.set_value(total, text="%.2f €" % total, currency="EUR", cell_type="float")
    row.set_cell(column, cell)
    row_number += 1
    table.set_row(row_number, row)

    # let merge some cells
    table.set_span((column - 3, row_number, column - 1, row_number), merge=True)

    row = Row()
    row.set_value(column - 1, "Total with tax:")
    total *= 1 + tax_rate
    cell = Cell()
    cell.set_value(total, text="%.2f €" % total, currency="EUR", cell_type="float")
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

    if not os.path.exists("test_output"):
        os.mkdir("test_output")

    output = os.path.join("test_output", "my_commercial.odt")

    commercial.save(target=output, pretty=True)
