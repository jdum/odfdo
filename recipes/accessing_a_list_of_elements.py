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
import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 75
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"


def read_source_document():
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def main():
    document = read_source_document()

    # The body object is an XML element from which we can access one or several
    # other elements we are looking for.
    body = document.body

    # Accessing a list of elements
    # Should you need to access all elements of a kind, there are the
    # get_xxxs methods, where xxx can be paragraph, heading, list, table, ...
    count_methods = " ".join(dir(body)).count("get_")
    print(f"{count_methods} get methods are available")
    # Some examples, that you can check against actual content of the odt file:
    # See how complex is our wikipedia documents:
    print("number of headings:", len(body.headers))
    print("number of images stored:", len(body.images))
    print("number of paragraphs:", len(body.paragraphs))
    print("number of links (URLs):", len(body.get_links()))
    print("number of footnotes:", len(body.get_notes()))
    # Our sample document has no table:
    # print("number of tables:", len(body.get_tables()))
    print("number of tables:", len(body.tables))

    # Each get_xxx_list method provides parameters for filtering the results.
    # For example headings can be listed by level, annotations by creator, etc.
    # Almost all of them accept filtering by style and content using a regular
    # expressions.
    print("Paragraphs with 'Fish':", len(body.get_paragraphs(content=r"Fish")))
    print(
        "Paragraphs with 'answer' and '42':",
        len(body.get_paragraphs(content=r"answer.*42")),
    )

    _expected_result = """
    96 get methods are available
    number of headings: 29
    number of images stored: 0
    number of paragraphs: 175
    number of links (URLs): 352
    number of footnotes: 49
    number of tables: 0
    Paragraphs with 'Fish': 4
    Paragraphs with 'answer' and '42': 1
    """

    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    body = document.body
    count_methods = " ".join(dir(body)).count("get_")
    assert count_methods == 96
    assert len(body.headers) == 29
    assert len(body.images) == 0
    assert len(body.paragraphs) == 175
    assert len(body.get_links()) == 352
    assert len(body.get_notes()) == 49
    assert len(body.get_paragraphs(content=r"Fish")) == 4
    assert len(body.get_paragraphs(content=r"answer.*42")) == 1


if __name__ == "__main__":
    main()
