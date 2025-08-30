#!/usr/bin/env python
"""Put an image in a Cell of a table of a spreadsheet.

Possible sequence of operations:

    - put image content in the Document,
    - put the image internal URI in a Frame,
    - adapt the Frame parameters
    - put the Frame in the Table
"""

import os
from pathlib import Path

from odfdo import Cell, Document, Element, Frame, Table

_DOC_SEQUENCE = 58
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "image_table_sheet"
TARGET = "spreadsheet.ods"
DATA = Path(__file__).parent / "data"
LOGO = DATA / "newlogo.png"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def add_row_style(document: Document, row_height: str) -> str:
    """Add some Row style to the document to adapt row height.

    Returns the style name"""
    style_def = f"""
    <style:style style:family="table-row">
        <style:table-row-properties style:row-height="{row_height}"
        fo:break-before="auto"/>
    </style:style>
    """
    style = Element.from_tag(style_def)
    style.name = f"row-height-{row_height}"
    # load the cell style in document
    document.insert_style(style, automatic=True)
    return style.name


def generate_document(image_path: Path, cell_coord: str) -> Document:
    document = Document("ods")
    body = document.body
    body.clear()

    table = Table("SomeTable")
    body.append(table)

    x, y = table._translate_cell_coordinates(cell_coord)

    # insert the image content in the document
    uri = document.add_file(image_path)

    # image must be embedded in a Frame
    # Use the "char" anchor
    image_frame = Frame.image_frame(uri, anchor_type="char")

    # adapt the Frame for the table context:
    width, height = image_frame.size
    image_frame.set_attribute("table:end-x", width)
    image_frame.set_attribute("table:end-y", height)
    address = f"{table.name}.{cell_coord}"
    image_frame.set_attribute("table:end-cell-address", address)

    # create a new Cell to receive the image:
    cell = Cell()
    cell.append(image_frame)

    # insert the cell in the table:
    table.set_cell(cell_coord, cell)

    # optional: apply to the row the height of the image:
    style_name = add_row_style(document, height)
    # here we specifies "clone=False" to interact with the inplace row, not a copy:
    row = table.get_row(cell_coord, clone=False)
    row.style = style_name

    return document


def main() -> None:
    document = generate_document(LOGO, "B2")
    test_unit(document, "B2")
    save_new(document, TARGET)


def test_unit(document: Document, coord: str) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table = document.body.get_table(0)
    cell = table.get_cell(coord)
    frame = cell.get_frames()[0]
    image = frame.images[0]
    url = image.url
    assert url.endswith("png")


if __name__ == "__main__":
    main()
