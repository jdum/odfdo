#!/usr/bin/env python
"""
Analyse a list of files and directory (recurse), open all ODF documents and copy pictures
from documents in a directory.
"""
import os
import optparse
from hashlib import sha1
import time

from odfdo import Document

#encoding = "UTF8"
default_dest_dir = "my_collected_pictures"
known_images = set()
counter_image = 0
counter_odf = 0
counter_outside = 0


def store_image(path, name, content, dest_dir=default_dest_dir):
    "image new name is odffile_imagename"
    dest_file = os.path.join(dest_dir, "%s_%s" %
                             (os.path.basename(path).replace('.', '_'), name))
    while os.path.exists(dest_file):
        dest_file += "_"
    with open(dest_file, 'wb') as f:
        f.write(content)
    global counter_image
    counter_image += 1


def parse_odf_pics(path, dest_dir=default_dest_dir):
    """ Using odfdo for:
            - open possible ODF document: Document (including URI)
            - find images inside the document: get_image_list, get_attribute
    """
    lst = os.path.basename(path).split(".")
    suffix = lst[-1].lower()
    if not suffix.startswith('od'):
        return
    try:
        document = Document(path)
    except:
        return
    global counter_odf
    global counter_outside
    counter_odf += 1
    for image in document.body.get_images():
        image_url = image.url
        if not image_url:
            continue
        try:
            image_content = document.get_part(image_url)
        except KeyError:
            print("- not found inside document:", path)
            print("  image URL:", image_url)
            counter_outside += 1
            continue
        image_name = image_url.split('/')[-1]
        if check_known(image_content):
            store_image(path, image_name, image_content, dest_dir)


def check_known(content):
    "remember already seen images by sha1 footprint"
    footprint = sha1(content).digest()
    if footprint in known_images:
        return False
    known_images.add(footprint)
    return True


if __name__ == '__main__':

    usage = "usage: %prog [options] <ODF documents dir>"
    description = "Retrieve images from several ODF sources."
    parser = optparse.OptionParser(usage, description=description)
    parser.add_option(
        "-d",
        "--directory",
        dest="directory",
        help="write images in DIRECTORY",
        action="store",
        type="string")
    options, sources = parser.parse_args()
    if not sources:
        print("Need some ODF source !")
        parser.print_help()
        exit(0)

    if options.directory:
        output_directory = options.directory
    else:
        output_directory = default_dest_dir
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    t0 = time.time()
    for source in sources:
        if os.path.isdir(source):
            for root, dirs, files in os.walk(source):
                for name in files:
                    parse_odf_pics(os.path.join(root, name), output_directory)
        else:
            parse_odf_pics(source, output_directory)
    elapsed = int(time.time() - t0)
    print("%s images copied (%s not found) from %s ODF files to %s in %ss." %
          (counter_image, counter_outside, counter_odf, output_directory,
           elapsed))
