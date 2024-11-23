"""Minimal example of how to add an footnote to a text document.
"""

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 47


def main():
    document = Document("text")
    body = document.body
    body.clear()

    paragraph = Paragraph("A paragraph with a footnote about some references.")
    body.append(paragraph)

    # Notes are quite complex so they deserve a dedicated API on paragraphs:
    paragraph.insert_note(
        after="graph",
        note_id="note1",
        citation="1",
        body='Author, A. (2007). "How to cite references" New York: McGraw-Hill.',
    )

    # That looks complex so we detail the arguments:
    #
    # after    =>   The word after what the “¹” citation is inserted.
    # note_id  =>	The unique identifier of the note in the document.
    # citation => 	The symbol the user sees to follow the footnote.
    # body 	   =>   The footnote itself, at the end of the page.
    #
    # odfdo creates footnotes by default. To create endnotes (notes
    # that appear at the end of the document), give the
    # note_class='endnote' parameter.


if __name__ == "__main__":
    main()
