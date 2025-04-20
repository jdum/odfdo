#!/usr/bin/env python
"""Each line of the text becomes a slide of the presentation, we change of style
depending on the length of text line.
"""
from pathlib import Path

from odfdo import Document, DrawPage, Frame, Style

_DOC_SEQUENCE = 287
# lst = open(sys.argv[1]).readlines()
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


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = generate_document()
    save_new(document, TARGET)


def generate_document():
    presentation = Document("presentation")
    body = presentation.body
    body.clear()

    # Creating a smooth style for the graphic item
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

    presentation.insert_style(base_style)

    # Making o lot of variations
    variants = [10, 11, 14, 16, 20, 24, 32, 40, 44]
    text_size = [95, 80, 65, 50, 40, 30, 20, 10, 5]
    for size in variants:
        variant_style = base_style.clone
        variant_style.set_attribute("style:name", f"Gloup{size}")
        variant_style.set_properties(area="text", size=f"{size}pt")
        presentation.insert_style(variant_style)

    for count, blurb in enumerate(CONTENT):
        text = blurb
        name = f"{count + 1} - { text[:10]}"
        page = DrawPage(name)
        # choosing some style:
        size = 48
        for index, max_size in enumerate(text_size):
            if len(text) > max_size:
                size = variants[index]
                break

        text_frame = Frame.text_frame(
            text,
            size=("24cm", "2cm"),
            position=("2cm", "8cm"),
            style=f"Gloup{size}",
            text_style=f"Gloup{size}",
        )

        page.append(text_frame)
        body.append(page)

    return presentation


if __name__ == "__main__":
    main()
