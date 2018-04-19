#!/usr/bin/env python
"""
Get the pictures from an .odt file.
"""
import os

from odfdo import Document

# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA)
# Remark: the document is badly made: the pictures are not displayed in the
# text, but are sill inside the document !
filename = "collection.odt"

doc = Document(filename)

# show the list the content of the document parts
parts = doc.get_parts()
print("Parts:")
print(parts)
print()

# We want the images of the document.
body = doc.body
pics = body.get_images()
print("Pics :")
print(pics)
print()

# we use the get_part function from odfdo to get the actual content
# of the image, to copy the images out of the .odt file:
if not os.path.exists('test_output'):
    os.mkdir('test_output')

new_dir = os.path.join('test_output', "my_document_pictures")
try:
    os.mkdir(new_dir)
except OSError:
    pass
for item in pics:
    # where is the image actual content in the file:
    uri = item.url
    image_content = doc.get_part(uri)
    image_filename = os.path.basename(uri)
    with open(os.path.join(new_dir, image_filename), 'wb') as f:
        f.write(image_content)

print("Files copied in %s:" % new_dir, os.listdir(new_dir))

expected_result = """
Parts:
['mimetype', 'styles.xml', 'content.xml', 'meta.xml',
'Pictures/12918371212580190208.jpe', 'Pictures/12918371212196450304.jpe',
'Pictures/12918371212102410240.jpe', 'Pictures/12918371212597118976.jpe',
'Pictures/12918371212184750080.jpe', 'Pictures/12918371212536940544.jpe',
'Pictures/12918371211855030272.jpe', 'Pictures/12918371212450449408.jpe',
'Pictures/12918371212741570560.jpe', 'META-INF/manifest.xml']

Pics :
[<odfdo.image.odf_image object at 0x1018e4390>, <odfdo.image.odf_image object at
0x1018e43d0>, <odfdo.image.odf_image object at 0x1018e4410>,
<odfdo.image.odf_image object at 0x1018e4450>, <odfdo.image.odf_image object at
0x1018e44d0>, <odfdo.image.odf_image object at 0x1018e4510>,
<odfdo.image.odf_image object at 0x1018e4550>, <odfdo.image.odf_image object at
0x1018e4590>, <odfdo.image.odf_image object at 0x1018e45d0>]

Files copied in my_document_pictures: ['12918371211855030272.jpe',
'12918371212102410240.jpe', '12918371212184750080.jpe',
'12918371212196450304.jpe', '12918371212450449408.jpe',
'12918371212536940544.jpe', '12918371212580190208.jpe',
'12918371212597118976.jpe', '12918371212741570560.jpe']
"""
