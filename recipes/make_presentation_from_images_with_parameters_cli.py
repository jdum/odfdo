#!/usr/bin/env python
"""
Create a presentation from a number of images in a given directory (specified
on the command line), where each image is put on the center of its own page
scaled to either: the maximum available size, prefered maximum size, or cover
the full page and lose some info. The image directory is not scanned
recursively, but you can add several directories, or the * meta character.
"""
import sys
import os
from optparse import OptionParser

from odfdo import Document, Frame, DrawPage

# Reading image size requires a graphic library
# The standard PIL lib may have different modules names on different OS
try:
    from PIL import Image

    PIL_ok = True
except:
    PIL_ok = False
    print("No image size detection. You should install Python Imaging Library")

# Global vars
output_file = ""
max_size = 0
crop_size = False

# Size (in cm) of a slide : (default page-layout)
slide_w, slide_h = 28.0, 21.0  # 4/3 screen
# FIXME: this is the default page-layout.
# - Changing the style of the page-layout by program is not done in this script
# - an other way, merging with external page-layout/master-page requires
#   extra files, out of the scope for this script.

# pool of images to insert in the presentation
images_pool = []


def read_image_size(path):
    try:
        w, l = Image.open(path).size
    except OSError:
        print("error reading", path)
        return None
    return (w, l)


# Main principe :
# - original image are left unmodified by the script
# - only the size they should appear is computed
# - later, the display engine (say LibreOffice) will merge this display
#   information with other informations, like the size of the page (page-layout)
#   and should act like a mask against the "big" croped image.
# - Test passed ok with OpenOffice3.2, LibreOffice3 beta1, LibreOffice 3.6.0
#   and NeoOffice3.1 (huhhhh, that's old!)
class ImageInfo:
    def __init__(self, path, size):
        self.path = path
        self.name = os.path.basename(path)
        self.width = size[0]  # pixel size
        self.height = size[1]
        if max_size:
            ratio = max(self.width / max_size, self.height / max_size)
            display_w = self.width / ratio
            display_h = self.height / ratio
        elif crop_size:
            ratio = min(self.width / slide_w, self.height / slide_h)
            display_w = self.width / ratio
            display_h = self.height / ratio
        else:
            ratio = max(self.width / slide_w, self.height / slide_h)
            display_w = self.width / ratio
            display_h = self.height / ratio
        self.disp_w = "%.2fcm" % display_w
        self.disp_h = "%.2fcm" % display_h
        self.pos_x = "%.2fcm" % ((slide_w - display_w) / 2)
        self.pos_y = "%.2fcm" % ((slide_h - display_h) / 2)
        print(self.name, self.disp_w, self.disp_h)


def add_image_to_pool(path):
    size = read_image_size(path)
    if size:
        images_pool.append(ImageInfo(path, size))


def collect_sources(args):
    for path in args:
        if os.path.isfile(path):
            add_image_to_pool(path)
            continue
        if os.path.isdir(path):
            for f in os.listdir(path):
                full_path = os.path.join(path, f)
                if os.path.isfile(full_path):
                    add_image_to_pool(full_path)


if __name__ == "__main__":
    usage = "usage: %prog -o FILE [options] <pict dir> <pict dir> ..."
    description = "Create a presentation from images."
    parser = OptionParser(usage, description=description)
    parser.add_option(
        "-o",
        "--output",
        dest="output",
        help="write output to OUTPUT",
        action="store",
        type="string",
    )
    parser.add_option(
        "-m",
        "--max",
        dest="crop",
        help="extend images on slide (default)",
        action="store_false",
    )
    parser.add_option(
        "-s",
        "--size",
        dest="size",
        help="max width in cm of the images",
        action="store",
        type="float",
    )
    parser.add_option(
        "-c",
        "--crop",
        dest="crop",
        help="crop images to use all space",
        action="store_true",
    )

    options, sources = parser.parse_args()
    if not sources or not options.output:
        print("need options !")
        parser.print_help()
        exit(0)
    if options.size:
        max_size = min(slide_h, options.size)
    else:
        if options.crop:
            crop_size = True

    output_file = options.output
    if not output_file.endswith(".odp"):
        output_file += ".odp"

    # Collecting images
    collect_sources(sources)
    if not images_pool:  # unable to find images
        print("no image found !")
        parser.print_help()
        exit(0)

    # Creation of the output Presentation document :
    # presentation = Document_from_type('presentation')  # 092
    presentation = Document("presentation")

    # Presentation got a body in which content is stored
    presentation_body = presentation.body

    # For each image, we create a page in the presentation and display the image
    # and some text on this frame
    for image in images_pool:
        # add the file to the document
        uri = presentation.add_file(image.path)

        # Create an underlying page for the image and the text
        page = DrawPage("Page " + image.name)

        # Create a frame for the image
        image_frame = Frame.image_frame(
            image=uri,
            name=image.name,
            text="",  # Text over the image object
            size=(image.disp_w, image.disp_h),  # Display size of image
            anchor_type="page",
            page_number=None,
            position=(image.pos_x, image.pos_y),
            style=None,
        )

        # Append all the component
        page.append(image_frame)
        presentation_body.append(page)

    # Finally save the result
    presentation.save(target=output_file, pretty=True)
