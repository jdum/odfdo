#!/usr/bin/env python

from odfdo import Document

# ODF export of Wikipedia article Hitchhiker's Guide to the Galaxy (CC-By-SA) :
filename = "collection2.odt"

doc = Document(filename)

# The body object is an XML element from which we can access one or several
# other elements we are looking for.
body = doc.body

# Should you be lost, remember elements are part of an XML tree:
mypara = body.get_paragraph(position=42)
print("children of the praragraph:", mypara.children)
print("parent of the paragraph:", mypara.parent)

# And you can introspect any element as serialized XML:
link0 = body.get_link(position=0)
print("Content of the serialization link:")
print(link0.serialize())
print("which is different from the text content of the link:")
print(link0.text_recursive)
