#!/usr/bin/env python
"""Insert a Table in a text document, then put an image in a Cell of the table.

Possible sequence of operations:

    - put image content in the Document,
    - put the image internal URI in a Frame,
    - put the Frame in a Paragraph,
    - put the Paragraph in a Cell,
    - put the Cell in a Table,
    - and Finally put the Table in the Document,
"""

import os
from pathlib import Path

from odfdo import Cell, Document, Element, Frame, Paragraph, Table

_DOC_SEQUENCE = 57
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "image_table"
TARGET = "document.odt"
DATA = Path(__file__).parent / "data"
LOGO = DATA / "newlogo.png"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def add_cell_style(document: Document) -> str:
    """Add some Cell style to the document.

    Returns the style name"""
    style_def = """
        <style:style style:family="table-cell"
        style:parent-style-name="Default">
        <style:table-cell-properties style:text-align-source="fix"/>
        <style:paragraph-properties fo:text-align="start"
        fo:margin-left="1mm"/>
        </style:style>
    """
    style = Element.from_tag(style_def)
    style.name = "left-align"
    # load the cell style in document
    document.insert_style(style, automatic=True)
    return style.name


def generate_document() -> Document:
    document = Document("text")
    body = document.body
    body.clear()

    table = Table("SomeTable", width=3, height=3)

    # insert the image content in the document
    uri = document.add_file(LOGO)

    # image must be embedded in a Frame
    # Use the "as-char" anchor
    image_frame = Frame.image_frame(uri, anchor_type="as-char", position=("0mm", "0mm"))

    # create a paragraph, and append image frame to it:
    para = Paragraph("Optional text", style="Standard")
    # add frame to the paragraph
    para.append(image_frame)

    # make a table Cell (with some style)
    style_name = add_cell_style(document)
    cell = Cell(style=style_name)

    # append the paragraph to cell:
    cell.append(para)

    # set the cell where you want in the table, here in "A1"
    table.set_cell((0, 0), cell)

    # add the table to the Document
    body.append(table)

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table = document.body.get_table(0)
    paragraph = table.get_cell("A1").paragraphs[0]
    frame = paragraph.get_frames()[0]
    image = frame.images[0]
    url = image.url
    assert url.endswith("png")


if __name__ == "__main__":
    main()
