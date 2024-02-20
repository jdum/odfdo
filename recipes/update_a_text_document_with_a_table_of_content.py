#!/usr/bin/env python
"""Update the table of contents of a document.
"""

from pathlib import Path

from odfdo import TOC, Document, Header, Paragraph

DATA = Path(__file__).parent / "data"
SOURCE = "doc_with_toc.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "modified_toc"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main() -> None:
    document = Document(DATA / SOURCE)
    update_toc(document)
    save_new(document, TARGET)


def update_toc(document: Document) -> None:
    check_toc_v1(document)
    add_some_header(document)
    check_toc_v2(document)
    change_toc_title(document)
    check_toc_v3(document)
    change_toc_title_to_empty(document)
    check_toc_v4(document)
    remove_second_header_1b(document)
    check_toc_v5(document)
    add_toc_title(document)
    check_toc_v6(document)


def check_toc_v1(document: Document) -> None:
    toc = document.body.get_toc()
    content = str(toc).split("\n")
    assert len(content) == 5
    assert content[0].startswith("Table of Contents")
    assert content[1].startswith("1. Lorem 1")
    assert content[2].startswith("1.1. Lorem 1A")
    assert content[3].startswith("1.2. Lorem 1B")
    assert content[4].startswith("1.3. Lorem 1C")


def add_some_header(document: Document) -> None:
    header = Header(1, "New header")
    document.body.append(header)
    document.body.append(Paragraph("Some text after the new header."))
    # update the table of contents
    toc = document.body.get_toc()
    toc.fill(document)


def check_toc_v2(document: Document) -> None:
    toc = document.body.get_toc()
    content = str(toc).split("\n")
    assert len(content) == 6
    assert content[0].startswith("Table of Contents")
    assert content[1].startswith("1. Lorem 1")
    assert content[2].startswith("1.1. Lorem 1A")
    assert content[3].startswith("1.2. Lorem 1B")
    assert content[4].startswith("1.3. Lorem 1C")
    assert content[5].startswith("2. New header")


def change_toc_title(document: Document) -> None:
    toc = document.body.get_toc()
    toc.set_toc_title("Another title")
    toc.fill(document)


def check_toc_v3(document: Document) -> None:
    toc = document.body.get_toc()
    content = str(toc).split("\n")
    assert len(content) == 6
    assert content[0].startswith("Another title")


def change_toc_title_to_empty(document: Document) -> None:
    toc = document.body.get_toc()
    toc.set_toc_title("")  # that will remove the title
    toc.fill(document)


def check_toc_v4(document: Document) -> None:
    toc = document.body.get_toc()
    content = str(toc).split("\n")
    assert len(content) == 5
    assert content[0].startswith("1. Lorem 1")
    assert content[1].startswith("1.1. Lorem 1A")
    assert content[2].startswith("1.2. Lorem 1B")
    assert content[3].startswith("1.3. Lorem 1C")
    assert content[4].startswith("2. New header")


def remove_second_header_1b(document: Document) -> None:
    # find second header:
    header = document.body.get_header(position=2)
    # this 'header' variable is attached to the document, so
    # deleting will remove the element from the document
    header.delete()

    toc = document.body.get_toc()
    toc.fill(document)


def check_toc_v5(document: Document) -> None:
    toc = document.body.get_toc()
    content = str(toc).split("\n")
    assert len(content) == 4
    assert content[0].startswith("1. Lorem 1")
    assert content[1].startswith("1.1. Lorem 1A")
    assert content[2].startswith("1.2. Lorem 1C")
    assert content[3].startswith("2. New header")


def add_toc_title(document: Document) -> None:
    toc = document.body.get_toc()
    toc.set_toc_title("A new title")
    toc.fill(document)


def check_toc_v6(document: Document) -> None:
    toc = document.body.get_toc()
    content = str(toc).split("\n")
    assert len(content) == 5
    assert content[0].startswith("A new title")
    assert content[1].startswith("1. Lorem 1")
    assert content[2].startswith("1.1. Lorem 1A")
    assert content[3].startswith("1.2. Lorem 1C")
    assert content[4].startswith("2. New header")


if __name__ == "__main__":
    main()
