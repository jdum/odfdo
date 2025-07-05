#!/usr/bin/env python
"""Create a presentation from a some images in a given directory,
where each image is put on the center of its own page scaled to either
the maximum available size, prefered maximum size, or cover the full
page and lose some info.
"""

import os
from pathlib import Path

# analyzing embedded image need Pillow library
from PIL import Image

from odfdo import Document, DrawPage, Frame

_DOC_SEQUENCE = 286
IMAGES = Path(__file__).parent / "data" / "images"
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "presentation_from_images"
TARGET = "presentation.odp"

MAX_SIZE = 15.0  # feel free to customize
CROP_SIZE = False  # feel free to customize

# Size (in cm) of a slide : (default page-layout)
SLIDE_W, SLIDE_H = 28.0, 21.0  # 4/3 screen

# FIXME: this is the default page-layout.
# - Changing the style of the page-layout by program is not done in this script
# - an other way, merging with external page-layout/master-page requires
#   extra files, out of the scope for this script.


def save_new(document: Document, name: str) -> None:
    """Save a recipe result Document."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    new_path = OUTPUT_DIR / name
    print("Saving:", new_path)
    document.save(new_path, pretty=True)


class ImageInfo:
    """Class to store informations about an image.

    Principle :
    - original image are left unmodified by the script
    - only the size they should appear is computed
    - later, the display engine (say LibreOffice) will merge this display
      information with other informations, like the size of the page
      (page-layout) and should act like a mask against the "big" croped image.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.size = None
        self.disp_w = self.disp_h = None
        self.pos_x = self.pos_y = None

    def adapt(self) -> bool:
        if not self.path.is_file():
            return False
        try:
            self.size = Image.open(self.path).size
        except OSError:
            # Not an image ?
            return False
        width, height = self.size
        if MAX_SIZE:
            ratio = max(width / MAX_SIZE, height / MAX_SIZE)
            display_w = width / ratio
            display_h = height / ratio
        elif CROP_SIZE:
            ratio = min(width / SLIDE_W, height / SLIDE_H)
            display_w = width / ratio
            display_h = height / ratio
        else:
            ratio = max(width / SLIDE_W, height / SLIDE_H)
            display_w = width / ratio
            display_h = height / ratio
        self.disp_w = f"{display_w:2f}cm"
        self.disp_h = f"{display_h:2f}cm"
        self.pos_x = f"{(SLIDE_W - display_w) / 2:2f}cm"
        self.pos_y = f"{(SLIDE_H - display_h) / 2:2f}cm"
        print(self.path.name, self.disp_w, self.disp_h)
        return True


def collect_images() -> list[ImageInfo]:
    pool = []
    for path in IMAGES.glob("**/*"):
        image_info = ImageInfo(path)
        if image_info.adapt():
            pool.append(image_info)
    return pool


def make_presentation(images_pool: list[ImageInfo]) -> Document:
    """Return a presentation made of images."""
    if not images_pool:  # unable to find images
        print("No image found !")
        return None

    presentation = Document("presentation")

    # Presentation got a body in which content is stored
    body = presentation.body
    body.clear()

    # For each image, we create a page in the presentation and display the image
    # and some text on this frame
    for image in images_pool:
        # add the file to the document
        uri = presentation.add_file(image.path)

        # Create an underlying page for the image and the text
        page = DrawPage(f"Page {image.path.name}")

        # Create a frame for the image
        image_frame = Frame.image_frame(
            image=uri,
            name=image.path.name,
            text="",  # Text over the image object
            size=(image.disp_w, image.disp_h),  # Display size of image
            anchor_type="page",
            page_number=None,
            position=(image.pos_x, image.pos_y),
            style=None,
        )

        page.append(image_frame)
        body.append(page)

    return presentation


def main() -> None:
    images_pool = collect_images()
    presentation = make_presentation(images_pool)
    if presentation is None:
        print("Something went wrong.")
        exit(0)
    test_unit(presentation)
    save_new(presentation, TARGET)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    body = document.body
    count = len([item for item in body.children if isinstance(item, DrawPage)])
    assert count == 3


if __name__ == "__main__":
    main()
