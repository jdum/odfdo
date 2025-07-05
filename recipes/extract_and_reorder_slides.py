#!/usr/bin/env python
"""Create a new presentation from a previous one by extracting some slides,
in a different order.
"""

import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 290
DATA = Path(__file__).parent / "data"
SOURCE = "presentation_base.odp"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "presentation_extracted"
TARGET = "presentation.odp"

SLIDES_ORDER = (3, 5, 2, 2)


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def extract_slides(presentation_base: Document) -> Document:
    """Return a new presentation from the slides of the base document
    by copying slides, in a different order.
    """
    extracted = Document("presentation")

    # Important, copy styles too:
    extracted.delete_styles()
    extracted.merge_styles_from(presentation_base)

    extracted.body.clear()
    for index in SLIDES_ORDER:
        try:
            slide_position = index - 1
            slide = presentation_base.body.get_draw_page(position=slide_position)
        except Exception:  # noqa: S112
            continue
        if slide is None:
            continue
        slide = slide.clone
        extracted.body.append(slide)

    return extracted


def main() -> None:
    document = read_source_document()
    extracted = extract_slides(document)
    test_unit(extracted)
    save_new(extracted, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    slides = document.body.get_draw_pages()
    assert len(slides) == len(SLIDES_ORDER)
    # slide content are ~their page number
    for idx, value in enumerate(SLIDES_ORDER):
        assert (str(slides[idx]).strip()) == str(value)


if __name__ == "__main__":
    main()
