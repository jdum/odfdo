#!/usr/bin/env python
"""Read a document from BytesIO."""

import io
import os
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 600
DATA = Path(__file__).parent / "data"
SOURCE = "lorem.odt"


def document_from_bytesio() -> Document:
    file_path = DATA / SOURCE
    with io.BytesIO() as bytes_content:
        # read the file in the BytesIO (or read from some network)
        bytes_content.write(file_path.read_bytes())
        # Create the odfdo.Document from the BytesIO
        bytes_content.seek(0)
        document = Document(bytes_content)
        return document


def main() -> None:
    document = document_from_bytesio()
    test_unit(document)


def test_unit(document: Document) -> None:
    # only for test suite:
    if "ODFDO_TESTING" not in os.environ:
        return

    assert document.body.search("Lorem ipsum dolor sit amet") is not None


if __name__ == "__main__":
    main()
