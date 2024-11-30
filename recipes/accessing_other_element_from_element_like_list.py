#!/usr/bin/env python
"""Accessing elements from element-like list.

Any fetched element is a XML tree context that can be queried, but only on the subtree it
contains. Here are quick examples of iteration on `Paragraphs` and `Lists` from the document.
"""
import os
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 80
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
    print("Number of available lists in the document:", len(body.lists))
    print()

    list4 = body.get_list(position=4)
    print(f"The 4th list contains {len(list4.paragraphs)} paragraphs")
    print()

    # Now print the list content
    paragraphs = list4.paragraphs
    for count, paragraph in enumerate(paragraphs):
        print(count + 1, ":", paragraph)

    _expected_result = """
    Number of available lists in the document: 5

    The 4th list contains 9 paragraphs

    1 : [BBC Cult website](http://www.bbc.co.uk/cult/hitchhikers/),
    official website for the [TV show version](http://en.wikipedia.org/w/index.php?title=The_Hitchhiker%27s_Guide_to_the_Galaxy_%28TV_series%29)
    (includes information, links and downloads)

    2 : [BBC Radio 4 website for the 2004–2005
    series](http://www.bbc.co.uk/radio4/hitchhikers/)

    3 : [Official Movie Site](http://hitchhikers.movies.go.com/)

    4 : [The Hitchhiker's Guide to the Galaxy
    (2005 movie)](http://www.imdb.com/title/tt0371724/)at the
    [Internet Movie Database](http://en.wikipedia.org/w/index.php?title=Internet_Movie_Database)

    5 : [The Hitch Hikers Guide to the Galaxy
    (1981 TV series)](http://www.imdb.com/title/tt0081874/)at the
    [Internet Movie Database](http://en.wikipedia.org/w/index.php?title=Internet_Movie_Database)

    6 : [h2g2](http://www.bbc.co.uk/h2g2/guide/)

    7 : [Encyclopedia of Television](http://www.museum.tv/archives/etv/H/htmlH/hitch-hickers/hitch-hickers.htm)

    8 : [British Film Institute Screen Online](http://www.screenonline.org.uk/tv/id/560180/index.html)
    page devoted to the TV series

    9 : [DC Comics H2G2 site](http://www.dccomics.com/graphic_novels/?gn=1816)
    """  # noqa: RUF001

    # only for test suite:
    if "ODFDO_TESTING" in os.environ:
        assert len(body.lists) == 5
        assert len(list4.paragraphs) == 9
        assert str(paragraphs[0]).startswith("[BBC Cult website](http")
        assert str(paragraphs[8]).startswith("[DC Comics H2G2 site](http")


def main():
    document = Document(SOURCE)
    analyse_list(document)


if __name__ == "__main__":
    main()
