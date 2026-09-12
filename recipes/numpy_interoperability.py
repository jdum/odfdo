#!/usr/bin/env python
"""Demonstrate interoperability between odfdo and NumPy."""

import os
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError:
    print("Warning: 'numpy' library is not available. Skipping recipe.")
    sys.exit(0)

from odfdo import Document

_DOC_SEQUENCE = 620
DATA = Path(__file__).parent / "data"
SOURCE = "store_table.ods"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "numpy"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def numpy_interoperability(document: Document) -> None:
    """Demonstrate converting between ODS data and NumPy arrays."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Extract numeric columns from ODS Table into 1D NumPy arrays
    table0 = document.body.tables[0]
    prices_raw = table0.to_dict(no_decimal=True)["price"]
    prices = np.array(prices_raw, dtype=float)

    print("--- 1. NumPy Array & Statistical Analysis ---")
    print("Prices array:", prices)
    print(f"Mean: {np.mean(prices):.2f}")
    print(f"Standard Deviation: {np.std(prices):.2f}")
    print(f"Min: {np.min(prices):.2f}, Max: {np.max(prices):.2f}")
    print(f"Sum: {np.sum(prices):.2f}")

    # 2. Build a 2D mathematical grid in NumPy and export to ODS
    print("\n--- 2. 2D NumPy Array -> ODS Table ---")
    x = np.linspace(0.0, 2.0 * np.pi, 5)
    sin_x = np.sin(x)
    cos_x = np.cos(x)
    calc_matrix = np.column_stack([x, sin_x, cos_x])

    headers = ["X (rad)", "sin(X)", "cos(X)"]
    trig_table_data = [
        headers,
        *[[round(val, 4) for val in row] for row in calc_matrix.tolist()],
    ]

    # 3. Convert a NumPy Structured Array into an ODS Table
    print("\n--- 3. NumPy Structured Array -> ODS Table ---")
    struct_arr = np.array(
        [
            ("Widget A", 19.99, 100),
            ("Widget B", 29.99, 50),
            ("Widget C", 9.99, 200),
        ],
        dtype=[("Product", "U20"), ("Price", "f8"), ("Stock", "i8")],
    )
    # Convert named fields to dictionary of lists
    structured_dict = {
        name: struct_arr[name].tolist() for name in (struct_arr.dtype.names or ())
    }

    # 4. Assemble multi-sheet ODS Document from NumPy computations
    out_doc = Document.from_dict(
        {
            "Trigonometry": trig_table_data,
            "StructuredInventory": structured_dict,
        }
    )

    print("\nTrigonometry Sheet (markdown):")
    print(out_doc.to_markdown()[0].content)
    print("\nStructured Inventory Sheet (markdown):")
    print(out_doc.to_markdown()[1].content)

    output_path = OUTPUT_DIR / "numpy_computations.ods"
    out_doc.save(output_path)
    print(f"\nSaved NumPy computations document to: {output_path}")


def main() -> None:
    document = read_source_document()
    numpy_interoperability(document)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table0 = document.body.tables[0]
    prices = np.array(table0.to_dict(no_decimal=True)["price"], dtype=float)
    assert np.isclose(np.mean(prices), 18.75)
    assert np.isclose(np.sum(prices), 56.25)

    # Test 2D array export
    data_2d = np.array([[1.0, 2.0], [3.0, 4.0]])
    doc_2d = Document.from_dict({"Matrix": [["A", "B"], *data_2d.tolist()]})
    assert doc_2d.to_dict()["Matrix"] == {"A": [1.0, 3.0], "B": [2.0, 4.0]}

    # Test structured array export
    s_arr = np.array([("a", 1), ("b", 2)], dtype=[("col1", "U10"), ("col2", "i4")])
    s_dict = {n: s_arr[n].tolist() for n in (s_arr.dtype.names or ())}
    doc_s = Document.from_dict(s_dict, table_name="Struct")
    assert doc_s.to_dict() == {"Struct": {"col1": ["a", "b"], "col2": [1, 2]}}


if __name__ == "__main__":
    main()
