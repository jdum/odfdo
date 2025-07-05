#!/usr/bin/env python
"""Minimal example of copy of a style from another document.

Document.get_style() main parameters:
family        : The family of the style, text styles apply on individual
                characters.
display_name  : The name of the style as we see it in a desktop
                application. Styles have an internal name
                (“Yellow_20_Highlight” in this example) but here we use
                the display_name instead.
"""

import os
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 310
DATA = Path(__file__).parent / "data"
SOURCE = "lpod_styles.odt"


def generate_document() -> Document:
    """Return a document with a style read from another document."""
    document = Document("text")
    body = document.body
    body.clear()

    styled_source = Document(DATA / SOURCE)
    highlight_style = styled_source.get_style(
        family="text", display_name="Yellow Highlight"
    )

    document.insert_style(highlight_style, automatic=True)

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    style = document.get_style(family="text", display_name="Yellow Highlight")
    assert style.display_name == "Yellow Highlight"


if __name__ == "__main__":
    main()
