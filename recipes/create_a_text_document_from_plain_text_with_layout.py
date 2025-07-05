#!/usr/bin/env python
"""Create a text document with custom styles. In this recipe, the styles
are created from their XML definition.

Steps:

 - Remove standard styles from the document,

 - set some styles grabed from a styles.xml ODF file (or generated),

 - insert plain "python" text, containing some \t , \n, and spaces.
"""

import os
from pathlib import Path

from odfdo import Document, Element, Paragraph, Style

_DOC_SEQUENCE = 60
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "styled2"
TARGET = "document.odt"


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def add_content(document: Document) -> None:
    """Add some styled content to the document."""

    # Some plain text :
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

    text_2 = (
        "Vestibulum                 "
        "ante               "
        "ipsum             primis\n"
        "in faucibus orci luctus et ultrices "
        "posuere cubilia Curae; Aliquam nibh."
    )

    text_3 = (
        "Duis semper. \n\tDuis arcu massa,"
        " \n\t\tscelerisque vitae, \n"
        "\t\t\tconsequat in, \n"
        "\t\t\t\tpretium a, enim. \n"
        "\t\t\t\t\tPellentesque congue. \n"
        "Ut in risus volutpat libero pharetra "
        "tempor. Cras vestibulum bibendum augue."
        "Praesent egestas leo in pede. Praesent "
        "blandit odio eu enim. Pellentesque sed"
    )

    # By default, paragraph text is added in "plain text" mode, so tabs or
    # line breaks are translated into the appropriate ODF structure.

    body = document.body

    paragraph = Paragraph(text_1, style="description")
    body.append(paragraph)

    paragraph = Paragraph(style="line")
    body.append(paragraph)

    paragraph = Paragraph(text_2, style="smallserif")
    body.append(paragraph)

    paragraph = Paragraph(style="line")
    body.append(paragraph)

    paragraph = Paragraph("A: " + text_3, style="description")
    # span offset become complex after inserting <CR> and <TAB> in a text
    paragraph.set_span("bolder", offset=5, length=6)  # find TEXT position 5 : 6
    paragraph.set_span("bolder", offset=18, length=4)  # find TEXT position 18 : 4
    paragraph.set_span("bolder", offset=49)  # find TEXT position 18 to the end
    # of the text bloc
    paragraph.set_span("bolder", regex=r"Praes\w+\s\w+")  # regex: Praes. + next word

    body.append(paragraph)

    paragraph = Paragraph(style="line")
    body.append(paragraph)

    # it is possible to add the content without the original layout (\n, tab, spaces)
    paragraph = Paragraph("B: " + text_3, style="description", formatted=False)
    body.append(paragraph)

    paragraph = Paragraph(style="line")
    body.append(paragraph)

    # text can also be append after paragraph creation
    paragraph = Paragraph(style="description")
    paragraph.append("C: " + text_3)
    body.append(paragraph)


def add_styles(document) -> None:
    """Add styles to the document from their XML definition."""

    # Element is the base class of all odfdo classes.
    # Element.from_tag permits the creation of any ODF XML tag

    # some font styles :
    style_font_1 = Element.from_tag(
        '<style:font-face style:name="OpenSymbol" svg:font-family="OpenSymbol"/>'
    )

    style_font_2 = Element.from_tag(
        '<style:font-face style:name="Liberation Serif" '
        'svg:font-family="Liberation Serif" '
        'style:font-family-generic="roman" '
        'style:font-pitch="variable"/>'
    )

    style_font_3 = Element.from_tag(
        '<style:font-face style:name="Liberation Sans" '
        'svg:font-family="Liberation Sans" '
        'style:font-family-generic="swiss" '
        'style:font-pitch="variable"/>'
    )

    # page layout style (changing margin)
    style_page = Element.from_tag(
        '<style:page-layout style:name="MyLayout">'
        '<style:page-layout-properties fo:page-width="21.00cm" '
        'fo:page-height="29.70cm" style:num-format="1" '
        'style:print-orientation="portrait" fo:margin-top="1.7cm" '
        'fo:margin-bottom="1.5cm" fo:margin-left="1.6cm" '
        'fo:margin-right="1.6cm" style:writing-mode="lr-tb" '
        'style:footnote-max-height="0cm"><style:footnote-sep '
        'style:width="0.018cm" style:distance-before-sep="0.10cm" '
        'style:distance-after-sep="0.10cm" style:line-style="solid" '
        'style:adjustment="left" style:rel-width="25%" '
        'style:color="#000000"/> </style:page-layout-properties>'
        "<style:footer-style> "
        '<style:header-footer-properties fo:min-height="0.6cm" '
        'fo:margin-left="0cm" fo:margin-right="0cm" '
        'fo:margin-top="0.3cm" style:dynamic-spacing="false"/> '
        "</style:footer-style></style:page-layout>"
    )

    # master style, using the precedent layout for the actual document
    style_master = Element.from_tag(
        '<style:master-page style:name="Standard" '
        'style:page-layout-name="MyLayout"><style:footer>'
        '<text:p text:style-name="Footer"> '
        "<text:tab/><text:tab/><text:page-number "
        'text:select-page="current"/> / <text:page-count '
        'style:num-format="1">15</text:page-count>'
        "</text:p></style:footer> "
        "</style:master-page>"
    )

    # some footer
    style_footer = Element.from_tag(
        '<style:style style:name="Footer" '
        'style:family="paragraph" style:class="extra" '
        'style:master-page-name="">'
        '<style:paragraph-properties style:page-number="auto" '
        'text:number-lines="false" text:line-number="0">'
        "<style:tab-stops>"
        '<style:tab-stop style:position="8.90cm" '
        'style:type="center"/>'
        '<style:tab-stop style:position="17.80cm" style:type="right"/>'
        "</style:tab-stops>"
        "</style:paragraph-properties>"
        "<style:text-properties "
        'style:font-name="Liberation Sans" '
        'fo:font-size="7pt"/></style:style>'
    )

    # some text style using Liberation Sans font
    style_description = Element.from_tag(
        '<style:style style:name="description" '
        'style:family="paragraph" '
        'style:class="text" style:master-page-name="">'
        "<style:paragraph-properties "
        'fo:margin="100%" fo:margin-left="0cm" fo:margin-right="0cm" '
        'fo:margin-top="0.35cm" fo:margin-bottom="0.10cm" '
        'style:contextual-spacing="false" '
        'fo:text-indent="0cm" '
        'style:auto-text-indent="false" '
        'style:page-number="auto"/>'
        "<style:text-properties "
        'style:font-name="Liberation Sans" '
        'fo:font-size="11pt"/>'
        "</style:style>"
    )

    # some text style using Liberation Serif font
    style_small_serif = Element.from_tag(
        '<style:style style:name="smallserif" '
        'style:family="paragraph" style:class="text">'
        '<style:paragraph-properties fo:margin="100%" '
        'fo:margin-left="1.20cm" '
        'fo:margin-right="0cm" fo:margin-top="0cm" '
        'fo:margin-bottom="0.10cm" '
        'style:contextual-spacing="false" '
        'fo:text-indent="0cm" '
        'style:auto-text-indent="false"/>'
        '<style:text-properties style:font-name="Liberation Serif" '
        'fo:font-size="9pt" '
        'fo:font-weight="normal"/>'
        "</style:style>"
    )

    # some style to have stylish line in text
    style_line = Element.from_tag(
        '<style:style style:name="line" '
        'style:family="paragraph" style:class="text">'
        '<style:paragraph-properties fo:margin="100%" '
        'fo:margin-left="0cm" '
        'fo:margin-right="0cm" fo:margin-top="0cm" '
        'fo:margin-bottom="0.15cm" '
        'style:contextual-spacing="false" fo:text-indent="0cm" '
        'style:auto-text-indent="false" fo:padding="0cm" '
        'fo:border-left="none" '
        'fo:border-right="none" fo:border-top="none" '
        'fo:border-bottom="0.06pt solid #000000"/>'
        '<style:text-properties style:font-name="Liberation Sans" '
        'fo:font-size="9pt"/>'
        "</style:style>"
    )

    # some odfdo generated style (for bold Span)
    style_bold = Style("text", name="bolder", bold=True)

    # remove default styles
    document.delete_styles()
    # add our styles
    document.insert_style(style_font_1, default=True)
    document.insert_style(style_font_2, default=True)
    document.insert_style(style_font_3, default=True)
    document.insert_style(style_page, automatic=True)
    document.insert_style(style_master)
    document.insert_style(style_footer)
    document.insert_style(style_description)
    document.insert_style(style_small_serif)
    document.insert_style(style_line)
    document.insert_style(style_bold)


def generate_document() -> Document:
    """Return  a text document with custom styles."""
    document = Document("text")
    document.body.clear()
    add_styles(document)
    add_content(document)
    return document


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    doc_styles_names = {s.name for s in document.get_styles()}
    assert len(doc_styles_names) == 11
    for name in ("bolder", "description", "line", "smallserif"):
        assert name in doc_styles_names
    paragraphs = document.body.paragraphs
    assert len(paragraphs) == 9
    para0 = paragraphs[0]
    assert "Lorem ipsum dolor" in str(para0)
    assert para0.style == "description"


if __name__ == "__main__":
    main()
