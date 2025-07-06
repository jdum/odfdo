#!/usr/bin/env python
"""Save a document as BytesIO."""

import io
import os
from pathlib import Path

from odfdo import Document, Paragraph

_DOC_SEQUENCE = 605
OUTPUT_DIR = Path(__file__).parent / "recipes_output" / "bytes"
TARGET = "document.odt"


def make_document() -> Document:
    """Return a Hello World document."""
    document = Document("text")
    body = document.body
    paragraph = Paragraph("Hello World")
    body.append(paragraph)
    return document


def document_to_bytesio(document: Document) -> bytes:
    with io.BytesIO() as bytes_content:
        document.save(bytes_content)
        # Now use the BytesIO in some way:
        # In a netwotk context, typically:
        #    response.write(bytes_content.getvalue())
        return bytes_content.getvalue()


def write_content(content: bytes) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / TARGET
    path.write_bytes(content)


def main() -> None:
    document = make_document()
    bytes_content = document_to_bytesio(document)
    test_unit(bytes_content)
    write_content(bytes_content)


def test_unit(content: bytes) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    with io.BytesIO() as bytes_content:
        bytes_content.write(content)
        bytes_content.seek(0)
        document = Document(bytes_content)
        assert document.body.search("Hello World") is not None


if __name__ == "__main__":
    main()
