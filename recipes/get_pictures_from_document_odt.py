#!/usr/bin/env python
"""Get all the pictures embeded in an .odt file.
"""
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


def read_source_document():
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def main():
    doc = read_source_document()
    # show the list the content of the document parts
    parts = doc.parts
    print("Parts:")
    print(pformat(parts))
    print()

    # We want the images of the document.
    body = doc.body
    found_pics = body.images
    print("Pics :")
    print(pformat(found_pics))
    print()

    # we use the get_part function from odfdo to get the actual content
    # of the image, to copy the images out of the .odt file:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for pic in found_pics:
        # where is the image actual content in the file:
        url = pic.url
        image_content = doc.get_part(url)
        origin_path = Path(url)
        destination_path = OUTPUT_DIR / origin_path.name
        destination_path.write_bytes(image_content)

    print(f"Files in {OUTPUT_DIR}:")
    for file in OUTPUT_DIR.glob("*"):
        print(file.name)


if __name__ == "__main__":
    main()
