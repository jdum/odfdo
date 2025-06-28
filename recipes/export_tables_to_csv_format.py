#!/usr/bin/env python
"""Export tables to CSV format."""

import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 610
DATA = Path(__file__).parent / "data"
SOURCE = "two_sheets.ods"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "csv"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def export_tables_to_csv(document: Document) -> None:
    """Export tables to CSV format."""
    for index, table in enumerate(document.body.tables):
        # default parameters produce an "excell" CSV format,
        # see Python csv library for options.
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / f"content_{index}.csv"
        table.to_csv(path)


def main() -> None:
    document = read_source_document()
    export_tables_to_csv(document)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    content0 = document.body.tables[0].to_csv()
    expected0 = "col A,col B,col C\r\n1,2,3\r\na text,,another\r\n"
    assert content0 == expected0

    content1 = document.body.tables[1].to_csv()
    expected1 = ",,,\r\n,col B,col C,col D\r\n,1,2,3\r\n,a text,,another\r\n"
    assert content1 == expected1


if __name__ == "__main__":
    main()
