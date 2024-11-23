#!/usr/bin/env python
"""Adding a table of content to an existing text document.
"""
from pathlib import Path

from odfdo import TOC, Document, Paragraph, Style

_DOC_SEQUENCE = 37
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "add_toc"
TARGET = "document.odt"
DATA = Path(__file__).parent / "data"
SOURCE = DATA / "collection.odt"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = Document(SOURCE)
    body = document.body

    # here is a way to insert a page break:
    page_break_style = Style("paragraph", name="page_break")
    page_break_style.set_properties({"fo:break-before": "page"})
    document.insert_style(page_break_style)
    empty_paragraph = Paragraph("", style="page_break")
    body.insert(empty_paragraph, 0)

    # The TOC element comes from the toc module
    toc = TOC()
    # to put the TOC at the end, just do:
    # body.append(toc)
    body.insert(toc, 0)
    # fill the toc with current content of document:
    toc.fill()

    save_new(document, TARGET)


if __name__ == "__main__":
    main()
