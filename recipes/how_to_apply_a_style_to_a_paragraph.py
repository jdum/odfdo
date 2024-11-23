"""Minimal example of how to add a styled paragraph to a document.
"""

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 335


def main():
    document = Document("text")
    body = document.body
    body.clear()

    # we knwo we have a style of name "highlight" :
    body.append(Paragraph("Highlighting the word", style="highlight"))


if __name__ == "__main__":
    main()
