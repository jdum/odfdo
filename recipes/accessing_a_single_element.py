#!/usr/bin/env python
"""Example of methods and properties to analyse a document.

These methods return a single element (or None):

    - `body.get_note(position)`
    - `body.get_paragraph(position)`
    - `body.get_header(position)`
"""

# Expected result on stdout:
# - Content of the first footnote:
# 1. [Gaiman, Neil](http://en.wikipedia.org/w/index.php?title=Neil_Gaiman)
# (2003). Don't Panic: Douglas Adams and the "Hitchhiker's Guide to the
# Galaxy". Titan Books. pp 144-145. ISBN 1-84023-742-2.
#
# - Content of the paragraph with the word 'Fish'
# In So Long, and Thanks for All the Fish (published in 1984), Arthur
# returns home to Earth, rather surprisingly since it was destroyed when
# he left. He meets and falls in love with a girl named
# [Fenchurch](http://en.wikipedia.org/w/index.php?title=Minor_characters_from_The_Hitchhiker%27s_Guide_to_the_Galaxy%23Fenchurch), and discovers this Earth is a replacement provided by the [dolphin](http://en.wikipedia.org/w/index.php?title=Dolphin)s in their Save the Humans campaign. Eventually he rejoins Ford, who claims to have saved the Universe in the meantime, to hitch-hike one last time and see God's Final Message to His Creation. Along the way, they are joined by Marvin, the Paranoid Android, who, although 37 times older than the universe itself (what with time
# travel and all), has just enough power left in his failing body to read
# the message and feel better about it all before expiring.
#
# - Content of the first Title:
# The Hitchhiker's Guide to the Galaxy
#
# - Content of the last Title:
# Official sites

import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 70
DATA = Path(__file__).parent / "data"
SOURCE = "collection2.odt"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def method_demo(document: Document) -> None:
    """Show some methos examples."""
    # The body object is an XML element from which we can access one or several
    # other elements we are looking for.
    body = document.body

    # Accessing a single element
    # To access a single element by name, position or a regular expression on
    # the content, use get_xxx_by_<criteria>, where criteria can be position,
    # content, or for some of them name, id title, description.
    print("- Content of the first footnote:")
    print(str(body.get_note(position=0)))
    print()
    print("- Content of the paragraph with the word 'Fish'")
    print(str(body.get_paragraph(content="Fish")))
    print("- Content of the first Title:")
    print(str(body.get_header(position=0)))
    print("- Content of the last Title:")
    print(str(body.get_header(position=-1)))


def main() -> None:
    document = read_source_document()
    method_demo(document)
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    body = document.body
    assert str(body.get_note(position=0)).startswith(
        "1. [Gaiman, Neil](http://en.wikipedia.org/w/index.php?title=Neil_Gaiman) (2003)"
    )
    assert str(body.get_paragraph(content="Fish")).endswith("all before expiring.\n")
    assert str(body.get_header(position=0)).startswith("The Hitchhiker's Guide")
    assert str(body.get_header(position=-1)).startswith("Official sites")


if __name__ == "__main__":
    main()
