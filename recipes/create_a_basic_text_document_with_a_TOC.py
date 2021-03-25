#!/usr/bin/env python
import os

# Uncommented parts are explained in: create_a_basic_text_document.py

# Some utilities
import urllib.request, urllib.parse, urllib.error


def random_text(sentences):
    uri = "http://enneagon.org/phrases/%s" % sentences
    try:
        text = urllib.request.urlopen(uri).read().decode("iso8859-1")
    except:
        text = "Almost no text."
    return text


from odfdo import Document, Header, Paragraph, TOC

# Create the document
my_document = Document("text")
body = my_document.body

# Create the Table Of Content
toc = TOC()
# Changing the default "Table Of Content" Title :
toc.title = "My Table of Content"

# Do not forget to add every components to the document:
body.append(toc)

# Add content (See Create_a_basic_document.py)
title1 = Header(1, random_text(1)[:70])
body.append(title1)
for p in range(3):
    title = Header(2, random_text(1)[:70])
    body.append(title)
    paragraph = Paragraph(random_text(10))
    body.append(paragraph)

# Beware, update the TOC with the actual content. If not done there,
# the reader will need to "update the table of content" later.
toc.fill()

if not os.path.exists("test_output"):
    os.mkdir("test_output")

output = os.path.join("test_output", "my_document_with_toc.odt")

# And finally save the document.
my_document.save(target=output, pretty=True)
