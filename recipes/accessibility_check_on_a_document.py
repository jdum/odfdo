#!/usr/bin/env python
"""Basic Accessibility test: check, for every picture in a document, if
there is:

  - a title (svg_title),
  - a description (svg_description)

or, at least, some caption text.

See test file `planes.odt` file and the result of the script.
"""
import os
import sys
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 200
DATA = Path(__file__).parent / "data"
SOURCE = "planes.odt"


def read_source_document():
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def main():
    doc = read_source_document()
    # We want the images of the document.
    body = doc.body
    images = body.images

    nb_images = len(images)
    nb_title = 0
    nb_description = 0
    nb_caption = 0

    for image in images:
        uri = image.url
        filename = uri.rpartition("/")[2]
        print(f"Image filename: {filename}")
        frame = image.parent
        name = frame.name
        title = frame.svg_title
        description = frame.svg_description
        if title:
            nb_title += 1
        if description:
            nb_description += 1
        print(f"Name: {name}, title: {title}, description: {description}")
        link = frame.parent
        # this part requires some ODF know how:
        if link.tag == "draw:a":
            caption = link.get_attribute("office:name")
            if caption:
                nb_caption += 1
                print(f"Caption: {caption}")
    print()
    print(f"The document displays {nb_images} pictures:")
    print(f" - pictures with a title: {nb_title}")
    print(f" - pictures with a description: {nb_description}")
    print(f" - pictures with a caption: {nb_caption}")

    _expected_result = """
    Image filename: 100000000000013B000000D345859F604DCE636A.jpg
    Name: graphics2, title: Spitfire, general view, description: Green spitfire in a hall, view from left front.
    Image filename: 100000000000013B000000D3F908DA0A939D2F4B.jpg
    Name: graphics3, title: Spitfire, detail, description: None
    Image filename: 100000000000013B000000D375CEBFD6D7CB7CE9.jpg
    Name: graphics1, title: None, description: None

    The document displays 3 pictures:
     - pictures with a title: 2
     - pictures with a description: 1
     - pictures with a caption: 0
    """

    # only for test suite:
    if "ODFDO_TESTING" in os.environ:
        assert nb_images == 3
        assert nb_title == 2
        assert nb_description == 1
        assert nb_caption == 0


if __name__ == "__main__":
    main()
