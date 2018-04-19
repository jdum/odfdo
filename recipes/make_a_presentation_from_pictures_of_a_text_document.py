#!/usr/bin/env python
"""
Open a .odt file with pictures in it, find and analyse all the images, create a
new .odp presentation, display all the pictures in the presentation, one image
per frame.
"""
import os

from urllib.request import urlopen
from urllib.parse import urlsplit

from odfdo import Document, Frame, DrawPage

# analysing embedded image need some special operation:
try:
    from PIL import Image
    PIL_ok = True
except:
    PIL_ok = False
    print("No image size detection. You should install Python Imaging Library")
if PIL_ok:
    import os
    from tempfile import mkstemp


# utilities
def embedded_image_ratio(href, part):
    if PIL_ok:
        image_suffix = '.' + href.split('.')[-1]
        fd, tmp_file = mkstemp(suffix=image_suffix)
        tmp_file_handler = os.fdopen(fd, 'wb')
        tmp_file_handler.write(part)
        tmp_file_handler.close()
        w, l = Image.open(tmp_file).size
        os.unlink(tmp_file)
        print("image %s , size : %sx%s" % (href, w, l))
        ratio = 1.0 * w / l
        return ratio
    else:
        return 1.0


# def Document_extend(filename):
#     result = urlsplit(filename)
#     scheme = result.scheme
#     if not scheme:
#         file = open(filename)
#     else:
#         file = urlopen(filename)
#     document = Document(file)  # open the document with odfdo
#     return document

# This the .odt file with some pictures in it we will display on a presentation
# filename = "collection.odt"
# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA)
filename = "collection.odt"
# For convenience, take it from the remote URI:
#filename="http://www.odfgr.org/wiki/example-wikipedia-article/;download"

# We will copy all image from collection.odt, build a presentation with the
# images and save it in this file:
output_filename = "my_presentation_of_text_picts.odp"

# Open the input document
# doc_source = Document_extend(filename)
doc_source = Document(filename)

# Making of the output Presentation document :
presentation_output = Document('presentation')

# Presentation got a body in which elements are stored
presentation_body = presentation_output.body
presentation_manifest = presentation_output.get_part('manifest')

# For each image, we create a page in the presentation and display the image
# and some text on this frame
# First, get all image elements available in document:
images_source = doc_source.body.get_images()
manifest_source = doc_source.get_part('manifest')

for image in images_source:
    # we use the get_part function from odfdo to get the actual content
    # of the images, with the URI link to the image as argument
    uri = image.url
    # weight = len(doc_source.get_part(uri))  # only for info
    # print "image %s , size in bytes: %s" % (uri, weight)
    part = doc_source.get_part(uri)  # actual image content
    name = uri.split('/')[-1]  # lets make a file name for image

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
        size=("%scm" % a, "%scm" % b),  # Display size of image
        anchor_type='page',
        page_number=None,
        position=('3.5cm', '3.5 cm'),
        style=None)

    # Add some text object somehere on the frame, with a text frame
    legend = "Image %s from Wikipedia document / %s" % (name, filename)
    text_frame = Frame.text_frame(
        legend,
        size=('26cm', '2cm'),
        position=('0.5cm', '0.5cm'),
        style="Standard",
        text_style="Standard")

    # Append all the component, do not forget to add the actuel image file
    # into the Picture global directory of the presentation file with set_part
    page.append(text_frame)
    page.append(image_frame)
    presentation_body.append(page)
    # for the same operation from a local filesystem image, just use:
    #presentation_output.add_file(uri)
    media_type = manifest_source.get_media_type(uri)
    presentation_manifest.add_full_path(uri, media_type)
    presentation_output.set_part(uri, doc_source.get_part(uri))

# Finally save the result

if not os.path.exists('test_output'):
    os.mkdir('test_output')

output = os.path.join('test_output', output_filename)

presentation_output.save(target=output, pretty=True)

expected_result = """
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
