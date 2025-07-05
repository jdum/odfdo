#!/usr/bin/env python
"""Demo of quick introspecting of a document's elements.

The body object of a document is a mapping of an XML tree from which we
can access other elements we are looking for (parent, children)."""

import os
import sys
from pathlib import Path
from pprint import pformat
from typing import Any

from odfdo import Document

_DOC_SEQUENCE = 480
DATA = Path(__file__).parent / "data"
# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA) :
SOURCE = "collection2.odt"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def analyser(document: Document) -> dict[str, Any]:
    """Return information from an element of the document."""

    result: dict[str, Any] = {}
    # Elements are part of an XML tree:
    paragraph = document.body.get_paragraph(position=42)

    result["tag"] = paragraph.tag
    result["attributes"] = paragraph.attributes
    result["str"] = str(paragraph)
    result["parent"] = paragraph.parent
    result["children"] = paragraph.children
    result["serialize"] = paragraph.serialize(pretty=True)

    print("Informations about the paragraph:")
    print(pformat(result))
    return result


def main() -> None:
    document = read_source_document()
    result = analyser(document)
    test_unit(result)


def test_unit(result: dict[str, Any]) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert result["tag"] == "text:p"
    assert repr(result["parent"]) == "<Element tag=text:note-body>"
    assert repr(result["children"]) == "[<Span tag=text:span>]"


if __name__ == "__main__":
    main()
