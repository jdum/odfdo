#!/usr/bin/env python
"""Concatenate several presentations (including presentations found in sub
directories), possibly merge styles and images. Result for style may vary.
"""
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 280
DATA = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "concatenate"
TARGET = "presentation.odp"


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = concatenate_presentations()
    save_new(document, TARGET)


def concatenate_presentations():
    concat_presentation = Document("presentation")
    concat_presentation.body.clear()
    concat_presentation.delete_styles()

    count = 0
    for presentation_path in DATA.glob("**/*.odp"):
        count += 1
        add_presentation(concat_presentation, presentation_path)

    nb_slides = len(concat_presentation.body.get_draw_pages())
    print(f"{count} presentations concatenated, {nb_slides} slides.")

    return concat_presentation


def add_presentation(concat_presentation, path):
    """Using odfdo for:
    - open .odp document
    - copy content and merge styles
    """
    try:
        document = Document(path)
    except Exception:
        return
    concat_presentation.merge_styles_from(document)
    # add all slides
    dest_body = concat_presentation.body
    dest_manifest = concat_presentation.manifest
    manifest = document.manifest
    slides = document.body.get_draw_pages()
    print(f"- {path.name} has {len(slides)} slides")
    for slide in slides:
        slide = slide.clone
        # dont forget images:
        for image in slide.images:
            uri = image.url
            media_type = manifest.get_media_type(uri)
            dest_manifest.add_full_path(uri, media_type)
            concat_presentation.set_part(uri, document.get_part(uri))
        # append slide, expecting nothing good about its final style
        dest_body.append(slide)


if __name__ == "__main__":
    main()
