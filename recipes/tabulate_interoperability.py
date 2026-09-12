#!/usr/bin/env python
"""Demonstrate formatting odfdo spreadsheet tables using tabulate."""

import os
import sys
from pathlib import Path

try:
    from tabulate import tabulate
except ImportError:
    print("Warning: 'tabulate' library is not available. Skipping recipe.")
    sys.exit(0)

from odfdo import Document

_DOC_SEQUENCE = 619
DATA = Path(__file__).parent / "data"
SOURCE = "store_table.ods"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "tabulate"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def tabulate_interoperability(document: Document) -> None:
    """Demonstrate rendering ODS tables in various text formats with tabulate."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    table0 = document.body.tables[0]

    # 1. Format using orient="list" (columnar dictionary) -> Grid table
    list_data = table0.to_dict(orient="list")
    print("--- 1. ASCII Grid Format (from orient='list') ---")
    grid_output = tabulate(list_data, headers="keys", tablefmt="grid")
    print(grid_output)

    # 2. Format using orient="records" (list of row dicts) -> Fancy Unicode Grid
    records_data = table0.to_dict(orient="records")
    print("\n--- 2. Fancy Unicode Grid Format (from orient='records') ---")
    fancy_output = tabulate(records_data, headers="keys", tablefmt="fancy_grid")
    print(fancy_output)

    # 3. Format using orient="matrix" (2D list) -> GitHub-flavored Markdown
    matrix_data = table0.to_dict(orient="matrix")[table0.name]
    print("\n--- 3. GitHub Markdown Format (from orient='matrix') ---")
    markdown_output = tabulate(matrix_data, headers="firstrow", tablefmt="github")
    print(markdown_output)

    # 4. Format all sheets in document -> HTML export
    html_sections: list[str] = []
    for table in document.body.tables:
        t_data = table.to_dict(orient="list")
        html_table = tabulate(t_data, headers="keys", tablefmt="html")
        html_sections.append(f"<h2>Table: {table.name}</h2>\n{html_table}")

    full_html = (
        "<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'>"
        "<title>ODS Export</title></head>\n<body>\n"
        + "\n<hr/>\n".join(html_sections)
        + "\n</body>\n</html>"
    )

    output_html_path = OUTPUT_DIR / "store_tables.html"
    output_html_path.write_text(full_html, encoding="utf-8")
    print(f"\nSaved HTML table report to: {output_html_path}")

    output_md_path = OUTPUT_DIR / "store_table.md"
    output_md_path.write_text(markdown_output + "\n", encoding="utf-8")
    print(f"Saved Markdown table to: {output_md_path}")


def main() -> None:
    document = read_source_document()
    tabulate_interoperability(document)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    table0 = document.body.tables[0]

    # Test orient="list" with grid format
    grid = tabulate(table0.to_dict(orient="list"), headers="keys", tablefmt="grid")
    assert "reference" in grid
    assert "white" in grid
    assert "25.75" in grid

    # Test orient="records" with pipe/github format
    pipe = tabulate(table0.to_dict(orient="records"), headers="keys", tablefmt="pipe")
    assert "| reference   | color   |   price |" in pipe
    assert "| ref01       | white   |   10    |" in pipe

    # Test orient="matrix" with firstrow headers
    matrix = table0.to_dict(orient="matrix")[table0.name]
    md = tabulate(matrix, headers="firstrow", tablefmt="github")
    assert "| reference   | color   |   price |" in md


if __name__ == "__main__":
    main()
