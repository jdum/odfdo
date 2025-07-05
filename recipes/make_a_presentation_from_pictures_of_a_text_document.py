#!/usr/bin/env python
"""Open a .odt file with pictures in it, find and analyse all the images,
create a new .odp presentation, display all the pictures in the presentation,
one image per frame.
"""

import io
import os
import sys
from pathlib import Path

# analyzing embedded image requires the Pillow library
from PIL import Image

from odfdo import Document, DrawPage, Frame

_DOC_SEQUENCE = 285
DATA = Path(__file__).parent / "data"
SOURCE = DATA / "collection.odt"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "presentation_images_in_odt"
TARGET = "presentation.odp"


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


def embedded_image_ratio(href: str, content: bytes) -> float:
    """Calculates the aspect ratio of an image content in bytes."""
    image_stream = io.BytesIO(content)
    img = Image.open(image_stream)
    width, height = img.size
    ratio = 1.0 * width / height
    print(f"Image {href}, size: {width}x{height}, ratio:{ratio:.2f}")
    return ratio


def compute_size(max_length: float, ratio: float) -> tuple[float, float]:
    """Compute the size the image will have from maximum length and ratio of dimensions
    of source image."""
    width = max_length * ratio
    height = max_length
    if ratio > 1.0:
        width /= ratio
        height /= ratio
    return width, height


def generate_document(source: Document) -> Document:
    """Return a presentation document made from pictures read from
    the source document."""
    # Making of the output Presentation document :
    presentation = Document("presentation")

    # Presentation got a body in which elements are stored
    presentation_body = presentation.body
    presentation_body.clear()
    presentation_manifest = presentation.manifest

    # For each image, we create a page in the presentation and display the image
    # and some text on this frame.
    # First, get all image elements available in document:
    images_source = source.body.images
    manifest_source = source.manifest

    for image in images_source:
        # we use the get_part function from odfdo to get the actual content
        # of the images, with the URI link to the image as argument
        uri = image.url
        # weight = len(doc_source.get_part(uri))  # only for info
        # print "image %s , size in bytes: %s" % (uri, weight)
        content: bytes = source.get_part(uri)  # actual image content
        name = uri.split("/")[-1]  # lets make a file name for image

        # Compute the display size of the image on the final page
        ratio = embedded_image_ratio(uri, content)
        # max size of the greatest side: 16 cm
        width, height = compute_size(16.0, ratio)

        # Create an underlying page for the image and the text
        page = DrawPage("page " + name)

        # Create a frame for the image
        image_frame = Frame.image_frame(
            image=uri,
            text="",  # Text over the image object
            size=(f"{width}cm", f"{height}cm"),  # Display size of image
            anchor_type="page",
            page_number=None,
            position=("3.5cm", "3.5 cm"),
            style=None,
        )

        # Add some text object somehere on the frame, with a text frame
        legend = f"Image {name} from Wikipedia document / {SOURCE.name}"
        text_frame = Frame.text_frame(
            legend,
            size=("26cm", "2cm"),
            position=("0.5cm", "0.5cm"),
            style="Standard",
            text_style="Standard",
        )

        # Append all the component, do not forget to add the actuel image file
        # into the Picture global directory of the presentation file with set_part
        page.append(text_frame)
        page.append(image_frame)
        presentation_body.append(page)

        # for the same operation from a local filesystem image, just use:
        # presentation_output.add_file(uri)
        media_type = manifest_source.get_media_type(uri)
        presentation_manifest.add_full_path(uri, media_type)
        # actually store the image content in the new document:
        presentation.set_part(uri, content)

    return presentation


def main() -> None:
    images_source = read_source_document()
    document = generate_document(images_source)
    test_unit(document)
    save_new(document, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert (len(document.body.images)) == 9
    assert (len(document.body.get_draw_pages())) == 9


if __name__ == "__main__":
    main()
