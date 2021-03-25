#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
This recipe caters for instance for the scenario where an organization
switches from one corporate logo to another, and has to replace the logo in
many thousands of existing documents.
"""

import os
import optparse
import time
from hashlib import sha1

from odfdo import Document

modified_file_suffix = "new"
counter_image = 0
counter_odf = 0
counter_hit = 0


def make_footprint(content):
    return sha1(content).digest()


def replace_odf_pics(path, old_footprint, new_content):
    """Using odfdo for:
    - open possible ODF document: Document
    - find images inside the document: get_images
    - replace images matching old_image by the new one
    """
    lst = os.path.basename(path).split(".")
    suffix = lst[-1].lower()
    if not suffix.startswith("od"):
        return
    try:
        document = Document(path)
    except:
        return
    global counter_image
    global counter_odf
    global counter_hit

    counter_odf += 1
    document_changed = False
    for image in document.body.get_images():
        image_url = image.url
        if not image_url:
            continue
        try:
            image_content = document.get_part(image_url)
        except KeyError:
            print("- not found inside document:", path, end=" ")
            print("  image URL:", image_url)
            continue
        counter_image += 1
        footprint = make_footprint(image_content)
        if footprint == old_footprint:
            counter_hit += 1
            document.set_part(image_url, new_content)
            document_changed = True
    if document_changed:
        lst = path.split(".")
        lst.insert(-1, modified_file_suffix)
        new_name = ".".join(lst)
        print(new_name)
        document.save(new_name)


if __name__ == "__main__":

    usage = "usage: %prog -o OLD_IMAGE -n NEW_IMAGE  ODF_sources"
    description = "Replace 'OLD' picture by 'NEW' picture in ODF sources."
    parser = optparse.OptionParser(usage, description=description)
    parser.add_option(
        "-o",
        "--old",
        dest="old_img",
        help="Old picture file name",
        action="store",
        type="string",
    )
    parser.add_option(
        "-n",
        "--new",
        dest="new_img",
        help="New picture file name",
        action="store",
        type="string",
    )

    options, sources = parser.parse_args()
    if not options.old_img:
        print("Need some old picture !")
        parser.print_help()
        exit(0)
    if not options.new_img:
        print("Need some new picture !")
        parser.print_help()
        exit(0)
    if not sources:
        print("Need some ODF source !")
        parser.print_help()
        exit(0)

    t0 = time.time()
    with open(options.old_img, "rb") as f:
        old_content_footprint = make_footprint(f.read())
    # making the new image content :
    buffer = Document("text")
    url = buffer.add_file(options.new_img)
    new_content = buffer.get_part(url)

    for source in sources:
        if os.path.isdir(source):
            for root, dirs, files in os.walk(source):
                for name in files:
                    replace_odf_pics(
                        os.path.join(root, name), old_content_footprint, new_content
                    )
        else:
            replace_odf_pics(source, old_content_footprint, new_content)
    elapsed = int(time.time() - t0)
    print(
        "%s images updated from %s images in %s ODF files in %s sec."
        % (counter_hit, counter_image, counter_odf, elapsed)
    )
