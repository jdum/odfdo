#!/usr/bin/env python
"""Retrieve all the pictures embeded in an .odt file."""

import os
import sys
from pathlib import Path
from pprint import pformat

from odfdo import Document

_DOC_SEQUENCE = 260
DATA = Path(__file__).parent / "data"
# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA)
# Remark: the document is badly made: the pictures are not displayed in the
# text, but are sill inside the document !
SOURCE = "collection.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "found_pics"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def read_pictures(document: Document) -> list[Path]:
    """Return the list of files retrieved from the document."""
    parts = document.parts
    print("ODF parts of the document:")
    print(pformat(parts))
    print()

    # we use the get_part function from odfdo to get the actual content
    # of the image, to copy the images out of the .odt file:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # images are DrawImage instances
    for draw_image in document.body.images:
        # where is the image actual content in the file:
        url = draw_image.url
        image_content = document.get_part(url)
        origin_path = Path(url)
        destination_path = OUTPUT_DIR / origin_path.name
        destination_path.write_bytes(image_content)

    result = sorted(OUTPUT_DIR.glob("*"))
    print(f"Picture files in {OUTPUT_DIR}:")
    for file in result:
        print(file.name)
    return result


def main() -> None:
    document = read_source_document()
    path_list = read_pictures(document)
    test_unit(path_list)


def test_unit(path_list: list[Path]) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(path_list) == 9


if __name__ == "__main__":
    main()
