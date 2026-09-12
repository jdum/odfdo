#!/usr/bin/env python
"""Demonstrate interoperability between odfdo and polars DataFrame."""

import os
import sys
from pathlib import Path

try:
    import polars as pl
except ImportError:
    print("Warning: 'polars' library is not available. Skipping recipe.")
    sys.exit(0)

from odfdo import Document

_DOC_SEQUENCE = 617
DATA = Path(__file__).parent / "data"
SOURCE = "store_table.ods"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "polars"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def polars_interoperability(document: Document) -> None:
    """Demonstrate reading ODS data into Polars and saving back to ODS."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Convert an odfdo Table to a polars DataFrame
    table0 = document.body.tables[0]
    df0 = pl.DataFrame(table0.to_dict(orient="list"), strict=False)
    print("Table 0 as Polars DataFrame:")
    print(df0)

    # 2. Convert entire Document (all sheets) to a dictionary of DataFrames
    doc_dict = document.to_dict(orient="list")
    dfs = {name: pl.DataFrame(data, strict=False) for name, data in doc_dict.items()}
    print("\nDocument Sheet Names:", list(dfs.keys()))
    for name, df in dfs.items():
        print(f"\nSheet '{name}':")
        print(df)

    # 3. Create a new DataFrame and convert it to an odfdo Document
    new_df = pl.DataFrame(
        {
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Price": [19.99, 29.99, 9.99],
            "Stock": [100, 50, 200],
        }
    )
    print("\nDocument from Polars DataFrame:")
    new_doc = Document.from_dict(
        new_df.to_dict(as_series=False),
        table_name="Inventory",
    )

    print(new_doc.to_markdown()[0].content)
    output_path = OUTPUT_DIR / "polars_inventory.ods"
    new_doc.save(output_path)
    print(f"\nSaved polars inventory document to: {output_path}")


def main() -> None:
    document = read_source_document()
    polars_interoperability(document)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    # Convert Table 0 to DataFrame and verify values
    table0 = document.body.tables[0]
    df0 = pl.DataFrame(table0.to_dict(orient="list"), strict=False)
    assert df0.columns == ["reference", "color", "price"]
    assert df0["reference"].to_list() == ["ref01", "ref02", "ref03"]

    # Create Document from DataFrame and verify
    data = {"City": ["Lyon", "Oslo"], "Code": [69, 47]}
    df = pl.DataFrame(data)
    doc = Document.from_dict(df.to_dict(as_series=False), table_name="Cities")
    assert doc.to_dict() == {"Cities": {"City": ["Lyon", "Oslo"], "Code": [69, 47]}}


if __name__ == "__main__":
    main()
