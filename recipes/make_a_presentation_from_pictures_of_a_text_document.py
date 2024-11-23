#!/usr/bin/env python
"""Open a .odt file with pictures in it, find and analyse all the images,
create a new .odp presentation, display all the pictures in the presentation,
one image per frame.
"""
import os
from pathlib import Path
from tempfile import mkstemp

# analyzing embedded image need Pillow library
from PIL import Image

from odfdo import Document, DrawPage, Frame

_DOC_SEQUENCE = 285
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "presentation_images_in_odt"
TARGET = "presentation.odp"
DATA = Path(__file__).parent / "data"
SOURCE = DATA / "collection.odt"


def embedded_image_ratio(href, part):
    image_suffix = "." + href.split(".")[-1]
    fd, tmp_file = mkstemp(suffix=image_suffix)
    tmp_file_handler = os.fdopen(fd, "wb")
    tmp_file_handler.write(part)
    tmp_file_handler.close()
    width, height = Image.open(tmp_file).size
    os.unlink(tmp_file)
    print(f"image {href} , size : {width}x{height}")
    ratio = 1.0 * width / height
    return ratio


def save_new(document: Document, name: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


def main():
    document = generate_document()
    save_new(document, TARGET)

    _expected_result = """
    image Pictures/12918371211855030272.jpe , size : 333x386
    image Pictures/12918371212102410240.jpe , size : 200x350
    image Pictures/12918371212184750080.jpe , size : 384x552
    image Pictures/12918371212196450304.jpe , size : 373x576
    image Pictures/12918371212450449408.jpe , size : 400x596
    image Pictures/12918371212536940544.jpe , size : 800x1195
    image Pictures/12918371212580190208.jpe , size : 561x282
    image Pictures/12918371212597118976.jpe , size : 660x515
    image Pictures/12918371212741570560.jpe , size : 328x504
    """


def generate_document():
    # Open the input document
    # doc_source = Document_extend(filename)
    doc_source = Document(SOURCE)

    # Making of the output Presentation document :
    presentation = Document("presentation")

    # Presentation got a body in which elements are stored
    presentation_body = presentation.body
    presentation_body.clear()
    presentation_manifest = presentation.manifest

    # For each image, we create a page in the presentation and display the image
    # and some text on this frame
    # First, get all image elements available in document:
    images_source = doc_source.body.images
    manifest_source = doc_source.manifest

    for image in images_source:
        # we use the get_part function from odfdo to get the actual content
        # of the images, with the URI link to the image as argument
        uri = image.url
        # weight = len(doc_source.get_part(uri))  # only for info
        # print "image %s , size in bytes: %s" % (uri, weight)
        part = doc_source.get_part(uri)  # actual image content
        name = uri.split("/")[-1]  # lets make a file name for image

        # Compute the display size of the image on the final page
        ratio = embedded_image_ratio(uri, part)
        max_border = 16.0  # max size of the greatest border, in cm
        a = max_border * ratio
        b = max_border
        if ratio > 1.0:
            a /= ratio
            b /= ratio

        # Create an underlying page for the image and the text
        page = DrawPage("page " + name)

        # Create a frame for the image
        image_frame = Frame.image_frame(
            image=uri,
            text="",  # Text over the image object
            size=(f"{a}cm", f"{b}cm"),  # Display size of image
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
        presentation.set_part(uri, doc_source.get_part(uri))

    return presentation


if __name__ == "__main__":
    main()
