#!/usr/bin/env python
"""
Basic Accessibility test: check, for every picture in a document, if there is:
- a title (svg_title),
- a description (svg_description)
or, at least, some caption text.
See planes.odt file and result of the script.
"""
import os

from odfdo import Document

filename = 'planes.odt'

doc = Document(filename)

# We want the images of the document.
body = doc.body
images = body.get_images()

nb_images = len(images)
nb_title = 0
nb_description = 0
nb_caption = 0

for image in images:
    uri = image.url
    filename = uri.split('/')[-1]
    print('Image filename:', filename)
    frame = image.parent
    name = frame.name
    title = frame.svg_title
    description = frame.svg_description
    if title:
        nb_title += 1
    if description:
        nb_description += 1
    print(f'Name: {name}, title: {title}, description: {description}')
    link = frame.parent
    # this part requires some ODF know how:
    if link.tag == 'draw:a':
        caption = link.get_attribute('office:name')
        if caption:
            nb_caption += 1
            print('Caption: ', caption)
print()
print(f'The document displays {nb_images} pictures:')
print(' - pictures with a title:', nb_title)
print(' - pictures with a description:', nb_description)
print(' - pictures with a caption:', nb_caption)

expected_result = """
Image filename: 100000000000013B000000D3AAA93FCC.jpg
Name: graphics2, title: Spitfire, general view, description: Green spitfire in a hall, view from left front.
Image filename: 100000000000013B000000D31365BB6C.jpg
Name: graphics3, title: Spitfire, detail, description: None
Image filename: 100000000000013B000000D367502732.jpg
Name: graphics1, title: None, description: None
Caption: Thunderbolt

The document displays 3 pictures:
 - pictures with a title: 2
 - pictures with a description: 1
 - pictures with a caption: 1
"""
