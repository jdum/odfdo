#!/usr/bin/env python
"""Read the text content from an .odt file.
"""
import sys
from pathlib import Path

from odfdo import Document

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
    doc = read_source_document()

    # just verify what type of document it is:
    print("Type of document:", doc.get_type())

    body = doc.body
    print(body)

    # to further manipulate the document, you can access to whole xml content:
    content = doc.content
    print(content)

    # A quick way to get the text content:
    text = doc.get_formatted_text()

    print("Size :", len(text))

    # Let's show the beginning :
    print(text[:320])


if __name__ == "__main__":
    main()
