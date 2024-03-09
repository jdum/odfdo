#!/usr/bin/env python
"""Accessing other element from element like list.
"""
import os
from pathlib import Path

from odfdo import Document

DATA = Path(__file__).parent / "data"
SOURCE = DATA / "collection2.odt"


def analyse_list(document):
    # The body object is an XML element from which we can access one or several
    # other elements we are looking for.
    body = document.body

    # Any element is a context for navigating but only on the subtree it
    # contains. Just like the body was, but since the body contains all content,
    # we didn't see the difference.
    # Let's try the lists:
    print("Number of available lists in the document:", len(body.get_lists()))
    print()

    list4 = body.get_list(position=4)
    print(f"The 4th list contains {len(list4.get_paragraphs())} paragraphs")
    print()

    # Now print the list content
    paragraphs = list4.get_paragraphs()
    for count, paragraph in enumerate(paragraphs):
        print(count + 1, ":", paragraph)
        print(paragraph.text_recursive)
        print()

    _expected_result = """
    Number of available lists in the document: 5

    The 4th list contains 9 paragraphs

    1 : <odfdo.paragraph.Paragraph object at 0x105761820> "text:p"
    BBC Cult website, official website for the TV show version (includes information, links and downloads)

    2 : <odfdo.paragraph.Paragraph object at 0x105761850> "text:p"
    BBC Radio 4 website for the 2004–2005 series

    3 : <odfdo.paragraph.Paragraph object at 0x105761880> "text:p"
    Official Movie Site

    4 : <odfdo.paragraph.Paragraph object at 0x1057618b0> "text:p"
    The Hitchhiker's Guide to the Galaxy (2005 movie) at the Internet Movie Database

    5 : <odfdo.paragraph.Paragraph object at 0x1057618e0> "text:p"
    The Hitch Hikers Guide to the Galaxy (1981 TV series) at the Internet Movie Database

    6 : <odfdo.paragraph.Paragraph object at 0x105761910> "text:p"
    h2g2

    7 : <odfdo.paragraph.Paragraph object at 0x105761940> "text:p"
    Encyclopedia of Television

    8 : <odfdo.paragraph.Paragraph object at 0x105761970> "text:p"
    British Film Institute Screen Online page devoted to the TV series

    9 : <odfdo.paragraph.Paragraph object at 0x1057617f0> "text:p"
    DC Comics H2G2 site

    """  # noqa: RUF001

    # only for test suite:
    if "ODFDO_TESTING" in os.environ:
        assert len(body.get_lists()) == 5
        assert len(list4.get_paragraphs()) == 9
        assert paragraphs[0].text_recursive.startswith("BBC Cult website")
        assert paragraphs[8].text_recursive.startswith("DC Comics H2G2")


def main():
    document = Document(SOURCE)
    analyse_list(document)


if __name__ == "__main__":
    main()
