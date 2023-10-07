#!/usr/bin/env python

import os

# Uncommented parts are explained in: create_a_basic_text_document.py
from odfdo import Document, Header, Paragraph

lorem_ipsum = open("./lorem.txt", "r", encoding="utf8").read()

# Create the document
my_document = Document("text")
body = my_document.body

# Add content (See Create_a_basic_document.py)
title1 = Header(1, "Main title")
body.append(title1)
for p in range(3):
    title = Header(2, f"title {p}")
    body.append(title)
    paragraph = Paragraph(lorem_ipsum[:240])

    # Adding Footnote
    # Now we add a footnote on each paragraph
    # Notes are quite complex so they deserve a dedicated API on paragraphs:
    some_word = paragraph.text_recursive.split()[3]
    # choosing the 4th word of the paragraph to insert the note
    paragraph.insert_note(
        after=some_word,  # The word after what the “¹” citation is inserted.
        note_id=f"note{p}",  # The unique identifier of the note in the document.
        citation="1",  # The symbol the user sees to follow the footnote.
        body=(
            f'Author{p}, A. (2007). "How to cite references", Sample Editions.'
            # The footnote itself, at the end of the page.
        ),
    )

    body.append(paragraph)

if not os.path.exists("test_output"):
    os.mkdir("test_output")

output = os.path.join("test_output", "my_document_with_footnote.odt")

# And finally save the document.
my_document.save(target=output, pretty=True)
