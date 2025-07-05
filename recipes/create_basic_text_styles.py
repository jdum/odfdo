#!/usr/bin/env python
"""Create basic text styles with the Style class API.

Styles are applied to entire paragraphs or headings, or to words using Span.

The create_style_steel() and create_style_special() functions below are
examples of styles that combine the area="text" and area="Graphic" or
area="paragraph" properties. The Style class API allows for basic styling,
but for more complex situations, it is recommended to use a document as a
template or copy the XML definition of an existing style. The recipe
change_paragraph_styles_methods.py shows these different methods.
"""

import os
from pathlib import Path

from odfdo import Document, Header, Paragraph, Style

_DOC_SEQUENCE = 330
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "basic_styles"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def create_style_header_blue(document: Document) -> None:
    """A style derived from the standard heading style.

    Bold blue font 160%, outline level 1
    """
    style = Style(
        family="paragraph",
        name="header_blue",
        display_name="header_blue",
        parent_style="Heading",
        area="text",
        bold=True,
        color="blue",
        size="160%",
    )
    style.set_attribute("style:default-outline-level", "1")
    document.insert_style(style)


def create_style_header_navy(document: Document) -> None:
    """A style derived from the standard heading style.

    Bold navy blue font 120%, outline Level 2
    """
    style = Style(
        family="paragraph",
        name="header_navy",
        display_name="header_navy",
        parent_style="Heading",
        area="text",
        bold=True,
        color="navy",
        size="120%",
    )
    style.set_attribute("style:default-outline-level", "2")
    document.insert_style(style)


def create_style_steel(document: Document) -> None:
    """A style derived from the standard text style.

    Yellow font on dark blue
    """
    style = Style(
        family="paragraph",
        area="text",
        name="steel",
        display_name="steel",
        color="yellow",
        background_color="darkblue",
    )
    style.set_properties(
        area="graphic",
        properties={
            "draw:fill": "solid",
            "draw:fill-color": "darkblue",
        },
    )
    document.insert_style(style)


def create_style_special(document: Document) -> None:
    """A style derived from the standard text style with fixed font.

    Courier New font, antique white background, 2cm margin and centered text
    """
    style = Style(
        family="paragraph",
        area="text",
        name="special",
        display_name="special",
        font="Courier New",
        font_family="Courier New",
        font_style_name="Regular",
        font_pitch="fixed",
        background_color="AntiqueWhite",
    )
    style.set_properties(
        area="paragraph",
        properties={
            "fo:margin-left": "2cm",
            "fo:margin-right": "2cm",
            "fo:line-height": "150%",
            "fo:text-align": "center",
        },
    )
    document.insert_style(style)


def create_style_bold_gold(document: Document) -> None:
    """A style derived from the standard text style.

    Bold font in dark goldenrod color
    """
    style = Style(
        family="text",
        name="bold_gold",
        display_name="bold_gold",
        bold=True,
        color="darkgoldenrod",
    )
    document.insert_style(style)


def create_style_italic_lime(document: Document) -> None:
    """An italic style derived from the standard text style.

    Font italic, size 120%, color lime green
    """
    style = Style(
        family="text",
        name="italic_lime",
        display_name="italic_lime",
        italic=True,
        size="120%",
        color="lime",
    )
    document.insert_style(style)


def add_styles(document: Document) -> None:
    """Add text styles to the document."""
    create_style_header_blue(document)
    create_style_header_navy(document)
    create_style_steel(document)
    create_style_special(document)
    create_style_bold_gold(document)
    create_style_italic_lime(document)


def add_content(document: Document) -> None:
    """Add some styled paragraphs and headers to the document."""
    body = document.body
    body.append(Header(1, "First level header", style="header_blue"))

    body.append(Header(2, "First sub header", style="header_navy"))
    para = Paragraph(
        "Lorem ipsum dolor sit amet, consectetuer "
        "adipiscing elit. Sed non risus. "
        "Suspendisse lectus tortor, dignissim sit amet, "
        "adipiscing nec, ultricies sed, dolor."
    )
    para.set_span("bold_gold", regex="dolor")
    para.set_span("italic_lime", regex=r"\w+ing")
    body.append(para)

    body.append(Header(2, "Second sub header", style="header_navy"))
    para = Paragraph(
        "Cras elementum ultrices diam. Maecenas ligula massa, "
        "varius a, semper congue, euismod non, mi. Proin porttitor, "
        "orci nec nonummy molestie, enim est eleifend mi, non "
        "fermentum diam nisl sit amet erat. Duis semper.",
        style="steel",
    )
    para.set_span("italic_lime", regex="semper")
    body.append(para)

    body.append(Header(2, "Third sub header", style="header_navy"))
    para = Paragraph(
        "Duis arcu massa, scelerisque vitae, consequat in, pretium a, "
        "enim. Pellentesque congue. Ut in risus volutpat libero "
        "pharetra tempor. Cras vestibulum bibendum augue. Praesent "
        "egestas leo in pede. Praesent blandit odio eu enim. "
        "Pellentesque sed dui ut augue blandit sodales.",
        style="special",
    )
    body.append(para)


def create_document() -> Document:
    """Generate a text Document with styles."""
    document = Document()
    body = document.body
    body.clear()
    add_styles(document)
    add_content(document)
    return document


def main() -> None:
    document = create_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    style1 = document.get_style("paragraph", "header_blue").serialize()
    assert 'name="header_blue"' in style1
    assert 'color="#0000FF"' in style1
    assert 'font-weight="bold"' in style1
    assert 'font-size="160%"' in style1

    style2 = document.get_style("paragraph", "header_navy").serialize()
    assert 'name="header_navy"' in style2
    assert 'color="#000080"' in style2
    assert 'font-weight="bold"' in style2
    assert 'font-size="120%"' in style2

    style3 = document.get_style("paragraph", "steel").serialize()
    assert 'name="steel"' in style3
    assert 'color="#FFFF00"' in style3
    assert "graphic-properties" in style3
    assert 'draw:fill-color="#00008B"' in style3

    style4 = document.get_style("paragraph", "special").serialize()
    assert 'name="special"' in style4
    assert 'background-color="#FAEBD7"' in style4
    assert "Courier" in style4
    assert 'line-height="150%"' in style4
    assert 'margin-left="2cm"' in style4
    assert 'margin-right="2cm"' in style4
    assert 'text-align="center"' in style4

    style5 = document.get_style("text", "bold_gold").serialize()
    assert 'name="bold_gold"' in style5
    assert 'color="#B8860B"' in style5
    assert 'font-weight="bold"' in style5

    style6 = document.get_style("text", "italic_lime").serialize()
    assert 'name="italic_lime"' in style6
    assert 'color="#00FF00"' in style6
    assert 'font-style="italic"' in style6
    assert 'font-size="120%"' in style6


if __name__ == "__main__":
    main()
