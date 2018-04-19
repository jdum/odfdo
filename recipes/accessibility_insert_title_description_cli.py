#!/usr/bin/env python
"""
This is a recipe for a standalone script that takes a set of documents, an image
and an alternative text description as its parameters. It updates any instance
of the image it finds in the document with the accessibility text provided.

 Exemple :

 ./accessibility_insert_title_description_cli.py \
    -i test_title_description/newlogo.png \
    -t "New Logo" \
    -d "new logo with blue background" \
    test_title_description/


 test_title/presentation2.new.odp
 test_title/text2.new.odt
 13 images updated from 13 images in 2 ODF files in 0 sec.

 Nota : odfdo currently can't directly acces images in styles / header
"""

import os
import optparse
import time
from hashlib import sha1

from odfdo import Document

modified_file_suffix = 'new'
counter_image = 0
counter_odf = 0
counter_hit = 0


def make_footprint(content):
    return sha1(content).digest()


def set_infos(path, chk_footprint, title, description):
    """ Using odfdo for:
            - open possible ODF document: Document
            - find images inside the document: get_images
            - set title and description if image matches
    """
    lst = os.path.basename(path).split('.')
    suffix = lst[-1].lower()
    if not suffix.startswith('od'):
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
            print(
                "- not found inside document:",
                path,
            )
            print("  image URL:", image_url)
            continue
        counter_image += 1
        footprint = make_footprint(image_content)
        if footprint == chk_footprint:
            counter_hit += 1
            frame = image.parent
            frame.svg_title = title
            frame.description = description
            document_changed = True
    if document_changed:
        lst = path.split('.')
        lst.insert(-1, modified_file_suffix)
        new_name = '.'.join(lst)
        print(new_name)
        document.save(new_name)


if __name__ == '__main__':

    usage = "usage: %prog -i IMAGE -t TITLE -d DESCRIPTION  ODF_sources"
    description = "Insert a TITLE and DESCRIPTION to any instance of the image."
    parser = optparse.OptionParser(usage, description=description)
    parser.add_option(
        "-i",
        "--image",
        dest="image",
        help="Image to look for in documents",
        action="store",
        type="string")
    parser.add_option(
        "-t",
        "--title",
        dest="title",
        help="Title of the image",
        action="store",
        type="string")
    parser.add_option(
        "-d",
        "--description",
        dest="description",
        help="Description of the image",
        action="store",
        type="string")

    options, sources = parser.parse_args()
    if not options.image:
        print("Need some image !")
        parser.print_help()
        exit(0)
    if not options.title:
        print("Need some title !")
        parser.print_help()
        exit(0)
    if not options.description:
        print("Need some description !")
        parser.print_help()
        exit(0)
    if not sources:
        print("Need some ODF source !")
        parser.print_help()
        exit(0)

    t0 = time.time()
    with open(options.image, 'rb') as f:
        content_footprint = make_footprint(f.read())

    for source in sources:
        if os.path.isdir(source):
            for root, dirs, files in os.walk(source):
                for name in files:
                    set_infos(
                        os.path.join(root, name), content_footprint,
                        options.title, options.description)
        else:
            set_infos(source, content_footprint, options.title,
                      options.description)
    elapsed = int(time.time() - t0)
    print("%s images updated from %s images in %s ODF files in %s sec." %
          (counter_hit, counter_image, counter_odf, elapsed))
