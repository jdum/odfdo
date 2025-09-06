#!/usr/bin/env python
"""Example of configuration of table position in a text document.

Contains methods for:

- table size,
- column width,
- table, row, column and cell styles.
"""

import os
from pathlib import Path

from odfdo import Document, Element, Paragraph, Style, Table

_DOC_SEQUENCE = 56
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "table_position"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def generate_document() -> Document:
    """Return a document with some tables."""
    document = Document("text")
    add_some_column_styles(document)
    add_some_row_styles(document)
    add_some_cell_styles(document)
    add_table_1(document)
    add_table_2(document)
    add_table_3(document)
    add_table_4(document)
    add_table_5(document)
    return document


def add_some_column_styles(document: Document) -> None:
    """Add 3 styles for columns of width 2cm, 3cm and 4cm.

    Note that columns do not contain cells, only styles
    """
    col_2cm_style = Style(family="table-column", name="col_2cm", width="2cm")
    col_3cm_style = Style(family="table-column", name="col_3cm", width="3cm")
    col_4cm_style = Style(family="table-column", name="col_4cm", width="4cm")
    document.insert_style(col_2cm_style, automatic=True)
    document.insert_style(col_3cm_style, automatic=True)
    document.insert_style(col_4cm_style, automatic=True)


def add_some_row_styles(document: Document) -> None:
    """Add a basic row style defining a small line height."""
    row_style = Style(family="table-row", name="row_17mm", height="17mm")
    document.insert_style(row_style, automatic=True)


def add_some_cell_styles(document: Document) -> None:
    """Add 2 cell styles, copied from XML definition in an ODF file."""
    cell_grid = """
         <style:style style:family="table-cell"
         style:parent-style-name="Default">
         <style:table-cell-properties
         fo:border="0.06pt solid #000000"/>
         <style:paragraph-properties
         fo:margin-left="1.2mm" fo:margin-right="1.2mm"/>
         </style:style>
    """
    style1 = Element.from_tag(cell_grid)
    style1.name = "cell_grid"
    document.insert_style(style1, automatic=True)

    cell_center_gray = """
         <style:style style:family="table-cell"
         style:parent-style-name="Default">
         <style:table-cell-properties
         fo:background-color="#dddddd" fo:border="0.06pt solid #000000"
         style:text-align-source="fix"/>
         <style:paragraph-properties fo:text-align="center"/>
         <style:text-properties fo:font-weight="bold"
         style:font-weight-asian="bold" style:font-weight-complex="bold"/>
         </style:style>
    """
    style2 = Element.from_tag(cell_center_gray)
    style2.name = "cell_center_gray"
    document.insert_style(style2, automatic=True)


def set_columns_width(table: Table) -> None:
    """For all table apply the same columns styles.

    Note that by default the returned column is a copy, so we need to
    use "table.set_column()" to apply the change in the table.
    """
    col = table.get_column("A")
    col.style = "col_2cm"
    col.repeated = 1
    table.set_column("A", col)

    col = table.get_column("B")
    col.style = "col_3cm"
    col.repeated = 1
    table.set_column("B", col)

    col = table.get_column("C")
    col.style = "col_4cm"
    col.repeated = 1
    table.set_column("C", col)


def set_rows_content(table: Table) -> None:
    """Load the row content."""
    for row in table.rows:
        row.style = "row_17mm"
        table.set_row(row.y, row)

    table.set_row_values(0, ["a1", "b1", "c1"])
    table.set_row_values(1, ["a2", "b2", "c2"])


def add_table_1(document: Document) -> None:
    """Add a Table example to the document."""
    tab_1_style = Style(
        family="table",
        name="tab_1",
        margin_left="1cm",
        margin_top="0.4cm",
        margin_bottom="1cm",
        width="9cm",
        align="left",
    )
    document.insert_style(tab_1_style, automatic=True)

    table_1 = Table(name="tab1", width=3, height=2, style="tab_1")

    set_columns_width(table_1)
    set_rows_content(table_1)

    body = document.body
    body.append(Paragraph("Table 1:"))
    body.append(Paragraph(" - margin_left:1cm, width: 9cm, align: left"))
    body.append(Paragraph(" - the sum of columns widths equals the table width"))
    body.append(table_1)


def add_table_2(document: Document) -> None:
    """Add a Table example to the document."""
    tab_2_style = Style(
        family="table",
        name="tab_2",
        margin_left="1cm",
        margin_top="0.4cm",
        margin_bottom="1cm",
        width="15cm",
        align="left",
    )
    document.insert_style(tab_2_style, automatic=True)

    table_2 = Table(name="tab2", width=3, height=2, style="tab_2")

    set_columns_width(table_2)
    set_rows_content(table_2)

    body = document.body
    body.append(Paragraph("Table 2:"))
    body.append(Paragraph(" - margin_left:1cm, width: 15cm, align: left"))
    body.append(
        Paragraph(
            " - the table width is greater than columns "
            "=> the columns are widened proportionally"
        )
    )
    body.append(table_2)


def add_table_3(document: Document) -> None:
    """Add a Table example to the document."""
    tab_3_style = Style(
        family="table",
        name="tab_3",
        margin_right="5cm",
        margin_top="0.4cm",
        margin_bottom="1cm",
        width="12cm",
        align="right",
    )
    document.insert_style(tab_3_style, automatic=True)

    table_3 = Table(name="tab3", width=3, height=2, style="tab_3")

    set_columns_width(table_3)
    set_rows_content(table_3)

    body = document.body
    body.append(Paragraph("Table 3:"))
    body.append(Paragraph(" - margin_right: not working, width: 12cm, align: right"))
    body.append(
        Paragraph(
            " - the table width is greater than columns "
            "=> the columns are widened proportionally"
        )
    )
    body.append(table_3)


def add_table_4(document: Document) -> None:
    """Add a Table example to the document."""
    tab_4_style = Style(
        family="table",
        name="tab_4",
        margin_top="0.4cm",
        margin_bottom="1cm",
        width="9cm",
        align="center",
    )
    document.insert_style(tab_4_style, automatic=True)

    table_4 = Table(name="tab4", width=3, height=2, style="tab_4")

    set_columns_width(table_4)
    set_rows_content(table_4)

    body = document.body
    body.append(Paragraph("Table 4:"))
    body.append(Paragraph(" - width: 9cm, align: center"))
    body.append(table_4)


def add_table_5(document: Document) -> None:
    """Add a Table example to the document."""
    tab_5_style = Style(
        family="table",
        name="tab_5",
        margin_top="0.4cm",
        margin_bottom="1cm",
        width="9cm",
        align="center",
    )
    document.insert_style(tab_5_style, automatic=True)

    table_5 = Table(name="tab4", width=3, height=2, style="tab_5")

    set_columns_width(table_5)
    set_rows_content(table_5)

    for cell in table_5.get_row(0, clone=False).iter_cells():
        cell.style = "cell_center_gray"
    for cell in table_5.get_row(1, clone=False).iter_cells():
        cell.style = "cell_grid"

    body = document.body
    body.append(Paragraph("Table 5:"))
    body.append(Paragraph(" - apply cell styles"))
    body.append(table_5)


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    for idx in range(5):
        table = document.body.get_table(idx)
        assert table.size == (3, 2)
        assert table.get_cell("A1").value == "a1"


if __name__ == "__main__":
    main()
