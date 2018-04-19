#!/usr/bin/env python
"""
Read the text content from an .odt file.
"""
# Import from odfdo
from odfdo import Document

# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA)
filename = "collection2.odt"

doc = Document(filename)

# just verify what type of document it is:
print("Type of document:", doc.get_type())

body = doc.body
print(body)

# to further manipulate the document, you can access to whole xml content:
content = doc.get_part('content.xml')
print(content)

# A quick way to get the text content:
text = doc.get_formatted_text()

print("Size :", len(text))

# Let's show the beginning :
print(text[:320])

expected_result = """
Type of document: text
<odfdo.element.odf_element object at 0x1018e4550> "office:text"
<odfdo.content.odf_content object at 0x1018e44d0>
Size : 54333
The Hitchhiker's Guide to the Galaxy

The Hitchhiker's Guide to the Galaxy is a science fiction comedy series created
by English writer, dramatist, and musician Douglas Adams. Originally a radio
comedy broadcast on BBC Radio 4 in 1978, it was later adapted to other formats,
and over several years it gradually became an
"""
