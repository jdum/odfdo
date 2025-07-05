#!/usr/bin/env python
"""Each line of the text becomes a slide of the presentation, we change of style
depending on the length of text line.
"""

import os
from pathlib import Path

from odfdo import Document, DrawPage, Frame, Style

_DOC_SEQUENCE = 287
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "styled_prez"
TARGET = "presentation.odp"

CONTENT = """123
azertyuiop
azertyuiop azertyuiop
azertyuiop azertyuiop azertyuiop
azertyuiop azertyuiop azertyuiop azertyuiop
azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop
azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop
azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop
azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop
azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop azertyuiop
end.
""".splitlines()

# If text length is bigger then first value, use second value as font size:
TEXT_LEN_FONT_SIZE = [
    (95, 10),
    (80, 11),
    (65, 14),
    (50, 16),
    (40, 20),
    (30, 24),
    (20, 32),
    (10, 40),
    (5, 44),
    (-1, 48),
]


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def create_base_style() -> Style:
    """Creating a smooth style for the graphic item."""
    base_style = Style(
        "graphic",
        name="Gloup48",
        parent="standard",
        stroke="none",
        fill_color="#b3b3b3",
        textarea_vertical_align="middle",
        padding_top="1cm",
        padding_bottom="1cm",
        padding_left="1cm",
        padding_right="1cm",
        line_distance="0cm",
        guide_overhang="0cm",
        guide_distance="0cm",
    )
    base_style.set_properties(area="paragraph", align="center")
    base_style.set_properties(
        area="text",
        color="#dd0000",
        text_outline="false",
        font="Liberation Sans",
        font_family="Liberation Sans",  # compatibility
        font_style_name="Bold",
        family_generic="swiss",
        size="48pt",
        weight="bold",
    )
    return base_style


def add_styles(document: Document) -> None:
    """Generate all styles usable by the presentation as variations of a
    base style."""
    base_style = create_base_style()
    for _, font_size in TEXT_LEN_FONT_SIZE:
        variant_style: Style = base_style.clone
        variant_style.set_attribute("style:name", f"Gloup{font_size}")
        variant_style.set_properties(area="text", size=f"{font_size}pt")
        document.insert_style(variant_style)


def generate_document() -> Document:
    """Generate a Presentation Document with different styles."""
    presentation = Document("presentation")
    body = presentation.body
    body.clear()

    add_styles(presentation)

    for count, blurb in enumerate(CONTENT):
        text = blurb
        name = f"{count + 1} - {text[:10]}"
        page = DrawPage(name)
        # choosing some style:
        for text_len, font_size in TEXT_LEN_FONT_SIZE:
            if len(text) > text_len:
                size = font_size
                break
        style_name = f"Gloup{size}"

        text_frame = Frame.text_frame(
            text,
            size=("24cm", "2cm"),
            position=("2cm", "8cm"),
            style=style_name,
            text_style=style_name,
        )

        page.append(text_frame)
        body.append(page)

    return presentation


def main() -> None:
    document = generate_document()
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    body = document.body
    count = len([item for item in body.children if isinstance(item, DrawPage)])
    assert count == len(CONTENT)
    first_page = body.children[0]
    assert str(first_page).strip() == CONTENT[0].strip()
    last_page = body.children[-1]
    assert str(last_page).strip() == CONTENT[-1].strip()


if __name__ == "__main__":
    main()
