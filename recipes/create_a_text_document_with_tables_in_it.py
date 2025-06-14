#!/usr/bin/env python
"""Build a commercial document, with numerical values displayed in
both the text and in a table.
"""

import os
from pathlib import Path

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


class Product:
    """Minimalistic Product."""

    def __init__(self, reference: int, name: str, price: float) -> None:
        self.reference = reference
        self.name = f"Product {name}"
        self.price = price


class OrderLine:
    """Line of an Order."""

    def __init__(self, reference: int, quantity: int) -> None:
        self.reference = reference
        self.quantity = quantity


def make_product_catalog() -> list[Product]:
    """Generate a list of Product."""
    catalog: list[Product] = []
    price = 10.0
    for index in range(5):
        catalog.append(Product(index, chr(65 + index), price))
        price += 10.5
    return catalog


def make_order(catalog: list[Product]) -> list[OrderLine]:
    """Generate purchase order list."""
    order: list[OrderLine] = []
    quantity = 1
    for product in catalog:
        quantity = int(quantity * 2.5)
        order.append(OrderLine(product.reference, quantity))
    return order


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def create_header_cell_style(doc: Document) -> str:
    """Create a Cell style, insert it in Document, return its name."""
    border = make_table_cell_border_string(thick="0.03cm", color="black")
    cell_style = create_table_cell_style(
        color="black",
        background_color=(210, 210, 210),
        border_right=border,
        border_left=border,
        border_bottom=border,
        border_top=border,
    )
    style_name = doc.insert_style(style=cell_style, automatic=True)
    return style_name


def add_top_content(doc: Document, catalog: list[Product]) -> None:
    """Add some descriptive content to the document."""
    body = doc.body

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


def add_order_table(
    doc: Document, catalog: list[Product], order: list[OrderLine]
) -> None:
    """Add a table with order lines."""
    body = doc.body
    title12 = Header(2, "Your order")
    body.append(title12)

    style_name = create_header_cell_style(doc)
    table = make_order_table(catalog, order, style_name)
    body.append(table)


def make_order_table(
    catalog: list[Product],
    order: list[OrderLine],
    style_name: str,
) -> Table:
    """Build the order table."""
    table = Table("Table")

    # Header of table
    row = Row()
    row.set_values(["Product", "Price", "Quantity", "Amount"])
    table.set_row("A1", row)
    # or: table.set_row(0, row)

    # Add a row for each order line
    row_number = 0
    for line in order:
        row_number += 1
        product = catalog[line.reference]

        row = Row()

        row.set_value("A", product.name)
        # or : row.set_value(0, product.name)

        cell = Cell()
        cell.set_value(
            product.price,
            text=f"{product.price:.2f} €",
            currency="EUR",
            cell_type="float",
        )
        row.set_cell("B", cell)
        # or : row.set_cell(1, cell)

        row.set_value("C", line.quantity)
        # row.set_value(2, line.quantity)

        price = product.price * line.quantity
        cell = Cell()
        cell.set_value(
            price,
            text=f"{price:.2f} €",
            currency="EUR",
            cell_type="float",
        )
        row.set_cell("D", cell)

        table.set_row(row_number, row)

    # Total lines

    # add a merged empty row
    row = Row()
    row_number += 1
    table.set_row(row_number, row)
    table.set_span((0, row_number, 3, row_number))

    # compute total line
    row = Row()
    row_number += 1
    row.set_value(0, "Total:")
    total = sum(table.get_column_values(3)[1:-1])
    # note: total is a Decimal
    cell = Cell()
    cell.set_value(
        total,
        text=f"{total:.2f} €",
        currency="EUR",
        cell_type="float",
    )
    row.set_cell(3, cell)
    table.set_row(row_number, row)
    # merge the 3 first columns for this row:
    table.set_span((0, row_number, 2, row_number), merge=True)

    # compute VAT line
    row = Row()
    row_number += 1
    row.set_value(0, "Total with tax:")
    total_vat = float(total) * (1 + TAX_RATE)
    cell = Cell()
    cell.set_value(
        total_vat,
        text=f"{total_vat:.2f} €",
        currency="EUR",
        cell_type="float",
    )
    row.set_cell(3, cell)
    table.set_row(row_number, row)
    table.set_span((0, row_number, 2, row_number), merge=True)

    # Let's add some style on header row
    row = table.get_row(0)
    for cell in row.traverse():
        cell.style = style_name
        row.set_cell(x=cell.x, cell=cell)
    table.set_row(row.y, row)

    return table


def generate_commercial(catalog: list[Product], order: list[OrderLine]) -> Document:
    """Generate a Text Document with table in in."""
    document = Document("text")
    add_top_content(document, catalog)
    add_order_table(document, catalog, order)

    return document


def main() -> None:
    catalog = make_product_catalog()
    order = make_order(catalog)
    document = generate_commercial(catalog, order)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table = document.body.get_table(name="Table")
    assert isinstance(table, Table)
    assert table.get_cell("A1").value == "Product"
    assert table.get_cell("A2").value == "Product A"
    assert table.get_cell("A8").value == "Total:"
    assert table.get_cell("B1").value == "Price"
    assert table.get_cell("C1").value == "Quantity"
    assert table.get_cell("C2").value == 2
    assert table.get_cell("D1").value == "Amount"


if __name__ == "__main__":
    main()
