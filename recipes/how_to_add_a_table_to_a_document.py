"""Minimal example of how to add a table to a text document.
"""
from odfdo import Document, Header, Paragraph, Table

_DOC_SEQUENCE = 55


def main():
    document = Document("text")
    body = document.body

    # Let's add another section to make our document clear:
    body.append(Header(1, "Tables"))
    body.append(Paragraph("A 3x3 table:"))

    # Creating a table :
    table = Table("Table 1", width=3, height=3)
    body.append(table)


if __name__ == "__main__":
    main()
