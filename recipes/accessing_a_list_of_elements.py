#!/usr/bin/env python
"""Example of methods and properties to analyse a document.

These methods or properties return a list of elements:

    - `body.headers`
    - `body.images`
    - `body.paragraphs`
    - `body.get_links()`
    - `body.get_notes()`
    - `body.tables`
    - `body.get_paragraphs(content)`
"""

# Expected result on stdout:
# 96 get methods are available
# number of headings: 29
# number of images stored: 0
# number of paragraphs: 175
# number of links (URLs): 352
# number of footnotes: 49
# number of tables: 0
# Paragraphs with 'Fish': 4
# Paragraphs with 'answer' and '42': 1

import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 75
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def analysis(document: Document) -> dict[str, int]:
    """Returns some statistics about the document."""
    result: dict[str, int] = {
        "methods": 0,
        "headings": 0,
        "images": 0,
        "paragraphs": 0,
        "links": 0,
        "footnotes": 0,
        "tables": 0,
        "fish": 0,
        "answer": 0,
    }

    # The body object is an XML element from which we can access one or several
    # other elements we are looking for.
    body = document.body

    # Accessing a list of elements
    # Should you need to access all elements of a kind, there are the
    # get_xxxs methods, where xxx can be paragraph, heading, list, table, ...
    # Methods without parameters are accessible through properties.
    result["methods"] = " ".join(dir(body)).count("get_")
    # Some examples, that you can check against actual content of the odt file:
    # See how complex is our wikipedia documents:
    result["headings"] = len(body.headers)
    result["images"] = len(body.images)
    result["paragraphs"] = len(body.paragraphs)
    result["links"] = len(body.get_links())
    result["footnotes"] = len(body.get_notes())
    # Our sample document has no table:
    # print("number of tables:", len(body.get_tables()))
    result["tables"] = len(body.tables)

    # Each get_xxx_list method provides parameters for filtering the results.
    # For example headings can be listed by level, annotations by creator, etc.
    # Almost all of them accept filtering by style and content using a regular
    # expressions.
    result["fish"] = len(body.get_paragraphs(content=r"Fish"))
    result["answer"] = len(body.get_paragraphs(content=r"answer.*42"))

    return result


def display_analysis(stats: dict[str, int]) -> None:
    """Print the stats on stdout."""
    print(f"{stats['methods']} get methods are available")
    print(f"number of headings: {stats['headings']}")
    print(f"number of images stored: {stats['images']}")
    print(f"number of paragraphs: {stats['paragraphs']}")
    print(f"number of links (URLs): {stats['links']}")
    print(f"number of footnotes: {stats['footnotes']}")
    print(f"number of tables: {stats['tables']}")
    print(f"Paragraphs with 'Fish': {stats['fish']}")
    print(f"Paragraphs with 'answer' and '42': {stats['answer']}")


def main() -> None:
    document = read_source_document()
    stats = analysis(document)
    display_analysis(stats)
    test_unit(stats)


def test_unit(stats: dict[str, int]) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert stats["methods"] == 96
    assert stats["headings"] == 29
    assert stats["images"] == 0
    assert stats["paragraphs"] == 175
    assert stats["links"] == 352
    assert stats["footnotes"] == 49
    assert stats["tables"] == 0
    assert stats["fish"] == 4
    assert stats["answer"] == 1


if __name__ == "__main__":
    main()
