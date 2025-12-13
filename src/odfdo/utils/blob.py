# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2013 Ars Aperta, Itaapy, Pierlis, Talend.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Authors (odfdo project): jerome.dumonteil@gmail.com
# The odfdo project is a derivative work of the lpod-python project:
# https://github.com/lpod/lpod-python
"""(Internal) Management of binary large objects (BLOBs), used by Document."""

from __future__ import annotations

import base64
import hashlib
from mimetypes import guess_type
from pathlib import Path
from typing import BinaryIO


class Blob:
    """Management of binary large objects (BLOBs).

    Attributes:
        content (bytes): The binary content of the blob.
        name (str): The name of the blob, typically generated from a hash
                    of the content.
        mime_type (str): The MIME type of the blob's content.
    """

    def __init__(self) -> None:
        """Initialise the Blob object."""
        self.content: bytes = b""
        self.name: str = ""
        self.mime_type: str = ""

    @classmethod
    def from_path(cls, path: str | Path) -> Blob:
        """Create a Blob from a file path.

        The blob's name is generated from a hash of its content, and the
        MIME type is guessed from the file extension.

        Args:
            path: The path to the file.

        Returns:
            A new Blob instance containing the file's content.
        """
        blob = cls()
        path = Path(path)
        blob.content = path.read_bytes()
        extension = path.suffix.lower()
        footprint = hashlib.shake_256(blob.content).hexdigest(16)
        blob.name = f"{footprint}{extension}"
        mime_type, _encoding = guess_type(blob.name)
        blob.mime_type = mime_type or "application/octet-stream"
        return blob

    @classmethod
    def from_io(
        cls, file_like: BinaryIO, mime_type: str = "application/octet-stream"
    ) -> Blob:
        """Create a Blob from a file-like object.

        The blob's name is generated from a hash of its content. The MIME type
        is set to a generic "application/octet-stream".

        Args:
            file_like: A file-like object opened in binary mode.
            mime_type: The MIME type of the blob's content.

        Returns:
            A new Blob instance containing the file's content.
        """
        blob = cls()
        blob.content = file_like.read()
        blob.name = hashlib.shake_256(blob.content).hexdigest(16)
        blob.mime_type = mime_type
        return blob

    @classmethod
    def from_base64(
        cls, b64string: str | bytes, mime_type: str = "application/octet-stream"
    ) -> Blob:
        """Create a Blob from a base64 encoded string.

        The blob's name is generated from a hash of its content.

        Args:
            b64string: The base64 encoded string.
            mime_type: The MIME type of the decoded content.

        Returns:
            A new Blob instance containing the decoded content.
        """
        blob = cls()
        blob.content = base64.standard_b64decode(b64string)
        blob.name = hashlib.shake_256(blob.content).hexdigest(16)
        blob.mime_type = mime_type
        return blob
