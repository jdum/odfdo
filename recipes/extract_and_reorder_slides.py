#!/usr/bin/env python
"""Create a new presentation from a previous one by extracting some slides,
in a different order.
"""
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 290
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "presentation_extracted"
TARGET = "presentation.odp"
DATA = Path(__file__).parent / "data"
SOURCE = DATA / "presentation_base.odp"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    new_order = (3, 5, 2, 2)
    presentation_base = Document(SOURCE)
    extracted = Document("presentation")

    # Important, copy styles too:
    extracted.delete_styles()
    extracted.merge_styles_from(presentation_base)
    extracted.body.clear()

    for index in new_order:
        try:
            slide_position = index - 1
            slide = presentation_base.body.get_draw_page(position=slide_position)
        except Exception:  # noqa: S112
            continue
        if slide is None:
            continue

        slide = slide.clone
        extracted.body.append(slide)

    save_new(extracted, TARGET)


if __name__ == "__main__":
    main()
