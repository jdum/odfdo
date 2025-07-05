#!/usr/bin/env python
"""Import a CSV file and load data into a table."""

import os
import sys
from pathlib import Path

from odfdo import Document, Table

_DOC_SEQUENCE = 615
DATA = Path(__file__).parent / "data"
SOURCE = "some_csv.csv"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "csv2"
TARGET = "document.ods"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def read_text_document() -> str:
    """Return the source text file."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Path(source).read_text()


def import_csv() -> Document:
    """Return a document containing an imported CSV content."""
    content = read_text_document()
    document = Document("ods")
    table = Table.from_csv(content, "Sheet name")
    document.body.clear()
    document.body.append(table)
    return document


def main() -> None:
    document = import_csv()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table = document.body.get_table(0)
    assert table.name == "Sheet name"
    expected = ",,,\r\n,col B,col C,col D\r\n,1,2,3\r\n,a text,,another\r\n"
    assert table.to_csv() == expected


if __name__ == "__main__":
    main()
