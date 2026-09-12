#!/usr/bin/env python
"""Demonstrate interoperability between odfdo and pandas DataFrame."""

import os
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Warning: 'pandas' library is not available. Skipping recipe.")
    sys.exit(0)

from odfdo import Document

_DOC_SEQUENCE = 615
DATA = Path(__file__).parent / "data"
SOURCE = "store_table.ods"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "pandas"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def pandas_interoperability(document: Document) -> None:
    """Demonstrate reading ODS data into Pandas and saving back to ODS."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Convert an odfdo Table to a pandas DataFrame
    table0 = document.body.tables[0]
    df0 = pd.DataFrame(table0.to_dict(orient="list"))
    print("Table 0 as DataFrame:")
    print(df0)

    # 2. Convert entire Document (all sheets) to a dictionary of DataFrames
    doc_dict = document.to_dict(orient="list")
    dfs = {name: pd.DataFrame(data) for name, data in doc_dict.items()}
    print("\nDocument Sheet Names:", list(dfs.keys()))

    # 3. Create a new DataFrame and convert it to an odfdo Document
    new_df = pd.DataFrame(
        {
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Price": [19.99, 29.99, 9.99],
            "Stock": [100, 50, 200],
        }
    )
    print("\nDocument from DataFrame")
    new_doc = Document.from_dict(
        new_df.to_dict(orient="list"),
        table_name="Inventory",
    )

    print(new_doc.to_markdown()[0].content)
    output_path = OUTPUT_DIR / "pandas_inventory.ods"
    new_doc.save(output_path)
    print(f"\nSaved pandas inventory document to: {output_path}")


def main() -> None:
    document = read_source_document()
    pandas_interoperability(document)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    # Convert Table 0 to DataFrame and verify values
    table0 = document.body.tables[0]
    df0 = pd.DataFrame(table0.to_dict(orient="list"))
    assert list(df0.columns) == ["reference", "color", "price"]
    assert df0["reference"].tolist() == ["ref01", "ref02", "ref03"]

    # Create Document from DataFrame and verify
    data = {"City": ["Lyon", "Oslo"], "Code": [69, 47]}
    df = pd.DataFrame(data)
    doc = Document.from_dict(df.to_dict(orient="list"), table_name="Cities")
    assert doc.to_dict() == {"Cities": {"City": ["Lyon", "Oslo"], "Code": [69, 47]}}


if __name__ == "__main__":
    main()
