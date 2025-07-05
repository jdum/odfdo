"""Minimal example of how to add a paragraph."""

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 12


def main() -> None:
    document = Document("text")
    body = document.body

    # create a new paragraph with some content :
    paragraph = Paragraph("Hello World")
    body.append(paragraph)


if __name__ == "__main__":
    main()
