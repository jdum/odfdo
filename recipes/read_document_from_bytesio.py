#!/usr/bin/env python
"""Read a document from BytesIO.
"""
import io
from pathlib import Path

from odfdo import Document

_DOC_SEQUENCE = 600
DATA = Path(__file__).parent / "data"
SOURCE = "lorem.odt"


def main():
    file_path = DATA / SOURCE
    with io.BytesIO() as bytes_content:
        # read the file in the BytesIO (or read from some network)
        bytes_content.write(file_path.read_bytes())
        # Create the odfdo.Document from the BytesIO
        bytes_content.seek(0)
        document = Document(bytes_content)
        # check :
        if document.body.search("Lorem ipsum dolor sit amet") is None:
            raise ValueError("string not found")


if __name__ == "__main__":
    main()
