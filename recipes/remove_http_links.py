#!/usr/bin/env python
"""Remove all the links (the text:a tag), keeping the inner text."""

import os
import sys
from pathlib import Path

from odfdo import Document, Link, remove_tree

_DOC_SEQUENCE = 510
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "nolink"
TARGET = "document.odt"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def remove_all_links(document: Document) -> list[tuple[str, int]]:
    """Remove all links and return statistics."""
    body = document.body
    result: list[tuple[str, int]] = []

    result.append(("source, links occurrences:", len(body.get_links())))
    remove_tree(body, Link)
    result.append(("final, links occurrences:", len(body.get_links())))

    for line in result:
        print(line[0], line[1])

    return result


def main() -> None:
    document = read_source_document()
    result = remove_all_links(document)
    test_unit(result)
    save_new(document, TARGET)


def test_unit(result: list[tuple[str, int]]) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert result[0][1] == 352
    assert result[1][1] == 0


if __name__ == "__main__":
    main()
