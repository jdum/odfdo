#!/usr/bin/env python
"""Basic Accessibility test: check, for every picture in a document, if
there is:

  - a title (svg_title),
  - a description (svg_description)

or, at least, some caption text.

See test file `planes.odt` file and the result of the script.
"""

# Expected result on stdout:
# The document displays 3 pictures:
#  - pictures with a title: 2
#  - pictures with a description: 1
#  - pictures with a caption: 0

# Image: 100000000000013B000000D345859F604DCE636A.jpg
#   Name: graphics2, Title: Spitfire, general view, Description:Green spitfire in a hall, view from left front., Caption:None
# Image: 100000000000013B000000D3F908DA0A939D2F4B.jpg
#   Name: graphics3, Title: Spitfire, detail, Description:None, Caption:None
# Image: 100000000000013B000000D375CEBFD6D7CB7CE9.jpg
#   Name: graphics1, Title: None, Description:None, Caption:None

import os
import sys
from pathlib import Path
from typing import Any

from odfdo import Document

_DOC_SEQUENCE = 200
DATA = Path(__file__).parent / "data"
SOURCE = "planes.odt"


def read_source_document() -> Document:
    """Return the source Document."""
    try:
        source = sys.argv[1]
    except IndexError:
        source = DATA / SOURCE
    return Document(source)


def accessibility_evaluator(document: Document) -> dict[str, Any]:
    """Count for each images: titles, caption,description."""
    result: dict[str, Any] = {
        "images": [],
        "titles": 0,
        "descriptions": 0,
        "captions": 0,
    }

    # We want the images of the document.
    body = document.body
    images = body.images

    for image in images:
        uri = image.url
        filename = uri.rpartition("/")[2]
        frame = image.parent
        name = frame.name
        title = frame.svg_title
        description = frame.svg_description
        link = frame.parent
        # this part requires some ODF know how:
        caption = None
        if link.tag == "draw:a":
            caption = link.get_attribute("office:name")

        result["images"].append(
            f"Image: {filename}\n"
            f"  Name: {name}, Title: {title}, "
            f"Description:{description}, Caption:{caption}"
        )
        if title:
            result["titles"] += 1
        if description:
            result["descriptions"] += 1
        if caption:
            result["captions"] += 1

    return result


def display_accessibilty(stats: dict[str, Any]) -> None:
    """Print the stats on stdout."""
    print(f"The document displays {len(stats['images'])} pictures:")
    print(f" - pictures with a title: {stats['titles']}")
    print(f" - pictures with a description: {stats['descriptions']}")
    print(f" - pictures with a caption: {stats['captions']}")
    print()
    for content in stats["images"]:
        print(content)


def main() -> None:
    document = read_source_document()
    stats = accessibility_evaluator(document)
    display_accessibilty(stats)
    test_unit(stats)


def test_unit(stats: dict[str, Any]) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert len(stats["images"]) == 3
    assert stats["titles"] == 2
    assert stats["descriptions"] == 1
    assert stats["captions"] == 0


if __name__ == "__main__":
    main()
