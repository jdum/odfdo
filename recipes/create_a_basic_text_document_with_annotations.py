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


from odfdo import Document, Header, Paragraph

# Create the document
my_document = Document("text")
body = my_document.body

# Add content (See Create_a_basic_document.py)
title1 = Header(1, random_text(1)[:70])
body.append(title1)
for p in range(3):
    title = Header(2, random_text(1)[:70])
    body.append(title)
    paragraph = Paragraph(random_text(10))

    # Adding Annotation
    # Annotations are notes that don’t appear in the document but
    # typically on a side bar in a desktop application. So they are not printed.

    # Now we add some annotation on each paragraph
    some_word = paragraph.text_recursive.split()[3]
    # choosing the 4th word of the paragraph to insert the note

    paragraph.insert_annotation(
        after=some_word,  # The word after what the annotation is inserted.
        body="It's so easy!",  # The annotation itself, at the end of the page.
        creator="Bob"  # The author of the annotation.
        # date= xxx              A datetime value, by default datetime.now().
    )

    body.append(paragraph)

if not os.path.exists("test_output"):
    os.mkdir("test_output")

output = os.path.join("test_output", "my_document_with_annotations.odt")

# And finally save the document.
my_document.save(target=output, pretty=True)
