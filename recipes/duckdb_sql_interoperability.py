#!/usr/bin/env python
"""Demonstrate SQL analytics on odfdo spreadsheets using DuckDB."""

import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

try:
    import duckdb
except ImportError:
    print("Warning: 'duckdb' library is not available. Skipping recipe.")
    sys.exit(0)

from odfdo import Document, Table

_DOC_SEQUENCE = 618
DATA = Path(__file__).parent / "data"
SOURCE = "store_table.ods"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "duckdb"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def _infer_sql_type(values: list[Any]) -> str:
    """Infer the best SQL column type from a list of cell values."""
    for v in values:
        if isinstance(v, (Decimal, float)):
            return "DOUBLE"
        if isinstance(v, bool):
            return "BOOLEAN"
        if hasattr(v, "isoformat"):
            return "DATE"
        if v is not None and not isinstance(v, int):
            return "VARCHAR"
    if any(isinstance(v, int) for v in values):
        return "BIGINT"
    return "VARCHAR"


def load_table_into_duckdb(
    con: duckdb.DuckDBPyConnection,
    table: Table,
) -> None:
    """Create a DuckDB table and insert rows from an odfdo Table."""
    matrix = table.to_dict(orient="matrix")[table.name]
    if not matrix:
        return
    headers = [str(h) for h in matrix[0]]
    data_rows = matrix[1:]
    if not data_rows:
        col_defs = ", ".join(f'"{h}" VARCHAR' for h in headers)
        con.execute(f'CREATE TABLE "{table.name}" ({col_defs})')
        return

    cols_data = [
        [row[i] if i < len(row) else None for row in data_rows]
        for i in range(len(headers))
    ]
    col_types = [_infer_sql_type(col) for col in cols_data]
    col_defs = ", ".join(f'"{h}" {t}' for h, t in zip(headers, col_types, strict=True))

    con.execute(f'CREATE TABLE "{table.name}" ({col_defs})')
    placeholders = ", ".join(["?"] * len(headers))
    con.executemany(
        f'INSERT INTO "{table.name}" VALUES ({placeholders})',  # noqa: S608
        [tuple(r) for r in data_rows],
    )


def duckdb_interoperability(document: Document) -> None:
    """Demonstrate querying ODS data with DuckDB SQL and saving results."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load all tables from the ODS Document into an in-memory DuckDB connection
    con = duckdb.connect()
    for table in document.body.tables:
        load_table_into_duckdb(con, table)

    print("Tables loaded into DuckDB:")
    con.sql("SHOW TABLES").show()

    # 2. Query a single table with SQL filtering
    print("\n--- Products with Price >= 20 ---")
    rel_products = con.sql(
        "SELECT reference, color, price FROM product WHERE price >= 20"
    )
    rel_products.show()

    # 3. Perform a SQL JOIN across spreadsheet sheets
    print("\n--- Inventory Valuation (JOIN 'product' and 'store') ---")
    query = """
        SELECT
            p.reference,
            p.color,
            p.price,
            s.quantity,
            s.available,
            (p.price * s.quantity) AS total_value
        FROM product p
        JOIN store s ON p.reference = s.reference
        WHERE s.available = true
        ORDER BY total_value DESC
    """
    rel_valuation = con.sql(query)
    rel_valuation.show()

    # 4. Convert SQL query results directly back to an odfdo Document
    result_matrix = [rel_valuation.columns] + [
        list(row) for row in rel_valuation.fetchall()
    ]
    valuation_doc = Document.from_dict({"Inventory_Valuation": result_matrix})

    print("\nResult Document (markdown):")
    print(valuation_doc.to_markdown()[0].content)

    output_path = OUTPUT_DIR / "duckdb_inventory_valuation.ods"
    valuation_doc.save(output_path)
    print(f"\nSaved DuckDB query result to: {output_path}")


def main() -> None:
    document = read_source_document()
    duckdb_interoperability(document)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    con = duckdb.connect()
    for table in document.body.tables:
        load_table_into_duckdb(con, table)

    # Verify tables
    tables = [r[0] for r in con.sql("SHOW TABLES").fetchall()]
    assert "product" in tables
    assert "store" in tables

    # Verify SQL query
    rel = con.sql("SELECT COUNT(*) FROM product WHERE price > 15")
    assert rel.fetchall()[0][0] == 2

    # Verify JOIN and export
    query = """
        SELECT p.reference, (p.price * s.quantity) AS total
        FROM product p
        JOIN store s ON p.reference = s.reference
        WHERE s.quantity > 0
        ORDER BY total DESC
    """
    rel_join = con.sql(query)
    rows = rel_join.fetchall()
    assert len(rows) == 2
    assert rows[0][0] == "ref02"
    assert rows[0][1] == 102.5

    matrix = [rel_join.columns] + [list(r) for r in rows]
    doc = Document.from_dict({"Valuation": matrix})
    assert doc.to_dict()["Valuation"]["reference"] == ["ref02", "ref01"]


if __name__ == "__main__":
    main()
