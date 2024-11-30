#!/usr/bin/env python
"""Demo of quick introspecting of a document's elements.
"""
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 480
DATA = Path(__file__).parent / "data"
# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA) :
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

    # Should you be lost, remember elements are part of an XML tree:
    para = body.get_paragraph(position=42)
    print("Children of the praragraph:\n   ", para.children)
    print("\nParent of the paragraph:\n   ", para.parent)

    # And you can introspect any element as serialized XML:
    link0 = body.get_link(position=0)
    print("\nContent of the serialization link:")
    print("   ", link0.serialize())
    print("\nWhich is different from the text content of the link:")
    print("   ", str(link0))


if __name__ == "__main__":
    main()
