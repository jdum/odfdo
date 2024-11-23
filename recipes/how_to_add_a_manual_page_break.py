#!/usr/bin/env python
"""Adding a manual page break to a text document.
"""
from pathlib import Path

from odfdo import Document, PageBreak, Paragraph, Style

_DOC_SEQUENCE = 95
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "page_break"
TARGET = "document.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = Document()
    body = document.body
    body.clear()

    # here a simple way to insert a page break with odfdoshortcuts:
    document.add_page_break_style()
    body.append(Paragraph("First paragraph"))
    body.append(PageBreak())
    body.append(Paragraph("Second paragraph"))

    # here is a different way to insert a page break:
    page_break_style = Style("paragraph", name="page_break_before")
    page_break_style.set_properties({"fo:break-before": "page"})
    document.insert_style(page_break_style)
    empty_paragraph = Paragraph("", style="page_break_before")
    body.append(empty_paragraph)
    body.append(Paragraph("Third paragraph"))

    save_new(document, TARGET)


if __name__ == "__main__":
    main()
