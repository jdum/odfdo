#!/usr/bin/env python
"""Save a document as BytesIO.
"""
import io
from pathlib import Path

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 605
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "bytes"
TARGET = "document.odt"


def make_document():
    document = Document("text")
    body = document.body
    paragraph = Paragraph("Hello World")
    body.append(paragraph)
    return document


def main():
    document = make_document()
    with io.BytesIO() as bytes_content:
        document.save(bytes_content)
        # Now use the BytesIO in some way:
        # In a netwotk context, typically:
        #    response.write(bytes_content.getvalue())
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_DIR / TARGET, "wb") as file:
            file.write(bytes_content.getvalue())


if __name__ == "__main__":
    main()
