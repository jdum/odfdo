"""Minimal example of how to add a Header of first level to a text document.
"""

from odfdo import Document, Header

_DOC_SEQUENCE = 67


def main():
    document = Document("text")
    body = document.body

    title1 = Header(1, "The Title")
    body.append(title1)


if __name__ == "__main__":
    main()
