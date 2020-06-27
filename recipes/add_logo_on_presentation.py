#!/usr/bin/env python
"""
Insert an image (e.g. the logo of an event, organization or a Creative Commons
attribution) with size x,y at position x2,y2 on a number of slides in a
presentation slide deck.

Exemple:

./add_logo_on_presentation.py -i newlogo.png -r 1-8 -s 4.00 presentation_logo.odp

"""

import sys
import os
from optparse import OptionParser

from odfdo import Document, Frame

# Readng image size requires a graphic library
# The standard PIL lib may have different modules names on different OS
try:
    from PIL import Image
    PIL_ok = True
except:
    PIL_ok = False
    print('No image size detection. '
          'You should install Python Imaging Library')

modified_file_suffix = 'new'
image_position = ('1.50cm', '1.50cm')
title = 'New Logo'
text = 'The new logo with blue background'


def make_image_size(path, size):
    try:
        w, h = Image.open(path).size
    except OSError:
        print('error reading', path)
        return None
    ratio = max(w / size, h / size)
    return (f'{w / ratio:.2f}cm', f'{h / ratio:.2f}cm')


def main():
    usage = 'usage: %prog -i IMAGE -r RANGE -s SIZE PRESENTATION'
    description = 'Add an image on some pages of a presentation.'
    parser = OptionParser(usage, description=description)
    parser.add_option(
        '-i',
        '--image',
        dest='image',
        help='Image to be added',
        action='store',
        type='string')
    parser.add_option(
        '-r',
        '--range',
        dest='range',
        help='Range of the slides',
        action='store',
        type='string')
    parser.add_option(
        '-s',
        '--size',
        dest='size',
        help='max width in cm of the image',
        action='store',
        type='float')

    options, source = parser.parse_args()
    if not source or not options.image or not options.range or not options.size:
        print('need options !')
        parser.print_help()
        exit(0)

    lst = options.range.split('-')
    start = int(lst[0]) - 1
    end = int(lst[1])
    file_name = source[0]
    image_size = make_image_size(options.image, float(options.size))

    presentation = Document(file_name)
    presentation_body = presentation.body

    uri = presentation.add_file(options.image)

    # Append all the component
    for i in range(start, end):
        # Create a frame for the image
        image_frame = Frame.image_frame(
            image=uri,
            text='',  # Text over the image object
            size=image_size,  # Display size of image
            anchor_type='page',
            page_number=None,
            position=image_position,
            style=None)
        image_frame.svg_title = title
        image_frame.svg_description = text
        slide = presentation_body.get_draw_page(position=i)
        slide.append(image_frame)

    # Finally save the result
    name_parts = file_name.split('.')
    name_parts.insert(-1, modified_file_suffix)
    new_name = '.'.join(name_parts)

    presentation.save(new_name)


if __name__ == '__main__':
    main()
