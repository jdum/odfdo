#!/usr/bin/env python
"""Minimal example of setting a page footer using Style.set_page_footer().

Note: the created footer uses the current footer style, to change that
footer style, use the method  set_footer_style() on the 'page-layout'
style family.
"""

import os
from pathlib import Path

from odfdo import Document, Header, Paragraph, Tab, VarPageNumber

_DOC_SEQUENCE = 62
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "styled4"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def make_document() -> Document:
    """Generate a short document with a page footer."""
    text_1 = (
        "Lorem ipsum dolor sit amet,\n\t"
        "consectetuer adipiscing elit.\n\tSed"
        "non risus.\n\tSuspendisse lectus tortor,\n"
        "ndignissim sit amet, \nadipiscing nec,"
        "\nultricies sed, dolor.\n\n"
        " Cras elementum ultrices diam. Maecenas ligula massa,"
        "varius a,semper congue, euismod non,"
        " mi. Proin porttitor, orci nec nonummy"
        "molestie, enim est eleifend mi,"
        " non fermentum diam nisl sit amet erat."
    )

    document = Document("text")
    body = document.body
    body.clear()
    body.append(Header(1, "Some Title"))
    body.append(Paragraph(text_1))

    # looking for the current "master-page" style, it is probably
    # named "Standard". If not found, search with something like:
    # print([s for s in document.get_styles() if s.family == "master-page"])
    page_style = document.get_style("master-page", "Standard")

    # The footer can be a Paragraph or a list of Paragraphs:
    first_line = Paragraph("\tA first footer line")
    second_line = Paragraph("Second line")
    second_line.append(Tab())
    second_line.append(Tab())
    second_line.append(VarPageNumber())
    second_line.append(".")
    my_footer = [first_line, second_line]

    page_style.set_page_footer(my_footer)

    # important: insert again the modified style
    document.insert_style(page_style)

    return document


def main() -> None:
    document = make_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return
    from odfdo import Style

    assert len([s for s in document.get_styles() if s.family == "master-page"]) >= 1
    page_style = document.get_style("master-page", "Standard")
    assert isinstance(page_style, Style)
    footer = page_style.get_page_footer()
    content = footer.serialize()
    assert "A first footer" in content
    assert "Second line" in content


if __name__ == "__main__":
    main()
