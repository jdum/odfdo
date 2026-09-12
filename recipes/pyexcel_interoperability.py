#!/usr/bin/env python
"""Demonstrate interoperability between odfdo and pyexcel."""

import os
import sys
from pathlib import Path

try:
    import pyexcel as pe
except ImportError:
    print("Warning: 'pyexcel' library is not available. Skipping recipe.")
    sys.exit(0)

from odfdo import Document

_DOC_SEQUENCE = 616
DATA = Path(__file__).parent / "data"
SOURCE = "store_table.ods"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "pyexcel"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def pyexcel_interoperability(document: Document) -> None:
    """Demonstrate reading ODS data into pyexcel and saving back to ODS."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Convert an odfdo Table to a pyexcel Sheet
    table0 = document.body.tables[0]
    matrix = table0.to_dict(orient="matrix")[table0.name]
    sheet0 = pe.Sheet(matrix, name=table0.name)
    print(f"Table 0 ('{table0.name}') as pyexcel Sheet:")
    print(sheet0)

    # 2. Convert entire Document (all sheets) to a pyexcel Book
    doc_matrix = document.to_dict(orient="matrix")
    book = pe.Book(doc_matrix)
    print("\nDocument Book Sheet Names:", book.sheet_names())
    for sheet in book:
        print(f"\nSheet '{sheet.name}':")
        print(sheet)

    # 3. Create new pyexcel Sheets and convert them to an odfdo Document
    inventory_sheet = pe.Sheet(
        [
            ["Product", "Price", "Stock"],
            ["Widget A", 19.99, 100],
            ["Widget B", 29.99, 50],
            ["Widget C", 9.99, 200],
        ],
        name="Inventory",
    )
    suppliers_sheet = pe.Sheet(
        [
            ["Supplier", "City"],
            ["Acme Corp", "Paris"],
            ["Global Goods", "Tokyo"],
        ],
        name="Suppliers",
    )

    # Convert single sheet to Document
    doc_from_sheet = Document.from_dict(
        {inventory_sheet.name: inventory_sheet.to_array()}
    )
    print("\nDocument from pyexcel Sheet (markdown):")
    print(doc_from_sheet.to_markdown()[0].content)

    # Convert pyexcel Book (multi-sheet) to Document
    new_book = pe.Book(
        {
            inventory_sheet.name: inventory_sheet,
            suppliers_sheet.name: suppliers_sheet,
        }
    )
    new_doc = Document.from_dict(new_book.to_dict())

    output_path = OUTPUT_DIR / "pyexcel_inventory.ods"
    new_doc.save(output_path)
    print(f"\nSaved pyexcel inventory document to: {output_path}")


def main() -> None:
    document = read_source_document()
    pyexcel_interoperability(document)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    # Convert Table 0 to pyexcel Sheet and verify values
    table0 = document.body.tables[0]
    matrix = table0.to_dict(orient="matrix")[table0.name]
    sheet0 = pe.Sheet(matrix, name=table0.name)
    assert sheet0.name == "product"
    assert sheet0.row[0] == ["reference", "color", "price"]
    assert sheet0.column[0] == ["reference", "ref01", "ref02", "ref03"]

    # Convert Document to pyexcel Book and verify
    doc_matrix = document.to_dict(orient="matrix")
    book = pe.Book(doc_matrix)
    assert book.sheet_names() == ["product", "store"]

    # Create Document from pyexcel Sheet and verify
    sheet = pe.Sheet([["City", "Code"], ["Lyon", 69], ["Oslo", 47]], name="Cities")
    doc_sheet = Document.from_dict({sheet.name: list(sheet.rows())})
    assert doc_sheet.to_dict() == {
        "Cities": {"City": ["Lyon", "Oslo"], "Code": [69, 47]}
    }

    # Create Document from pyexcel Book and verify
    doc_book = Document.from_dict(book.to_dict())
    assert "product" in doc_book.to_dict()
    assert "store" in doc_book.to_dict()


if __name__ == "__main__":
    main()
