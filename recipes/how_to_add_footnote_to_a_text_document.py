#!/usr/bin/env python
"""Minimal example of how to add an footnote to a text document.

Notes are quite complex so they deserve a dedicated API on paragraphs:

paragraph.insert_note()

The arguments are:

after    =>   The word after what the “¹” citation is inserted.
note_id  =>	  A unique identifier of the note in the document.
citation =>   The symbol the user sees to follow the footnote.
body 	 =>   The footnote itself, at the end of the page.

odfdo creates footnotes by default. To create endnotes (notes
that appear at the end of the document), add the parameter:
note_class='endnote'.
"""

import os

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 47


def generate_document() -> Document:
    """Return a document with a footnote."""
    document = Document("text")
    body = document.body
    body.clear()

    paragraph = Paragraph("A paragraph with a footnote about some references.")
    body.append(paragraph)

    paragraph.insert_note(
        after="graph",
        note_id="note1",
        citation="1",
        body='John Doe (2007). "How to cite references" New York: Books.',
    )

    return document


def main() -> None:
    document = generate_document()
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    notes = document.body.get_notes()
    assert len(notes) == 1
    assert notes[0].note_id == "note1"


if __name__ == "__main__":
    main()
