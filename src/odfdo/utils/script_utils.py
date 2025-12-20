# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""Utility functions for command-line scripts that handle ODF documents.

This module provides helpers for common script tasks, such as reading a
document from a file path or standard input, and saving a document to a file
path or standard output.
"""

from __future__ import annotations

import io
import selectors
import sys

from odfdo import Document

STDIN_TIMEOUT = 0.5


def detect_stdin_timeout() -> None:  # pragma: no cover
    """Detects if data is available on standard input within a timeout.

    This function is used to prevent scripts from blocking indefinitely when
    expecting input from stdin. It is not supported on Windows.

    Raises:
        ValueError: If no data is available on stdin after the timeout.
    """
    if sys.platform == "win32":
        # cant do that on windows
        return  # pragma: no cover
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin, selectors.EVENT_READ)
    something = selector.select(timeout=STDIN_TIMEOUT)
    if not something:
        raise ValueError("Timeout reading from stdin")
    selector.close()


def read_document(input_path: str | None) -> Document:
    """Reads an ODF document from a file path or standard input.

    If `input_path` is provided, the document is loaded from that file.
    Otherwise, the document is read from the standard input stream.

    Args:
        input_path: The path to the input ODF file.

    Returns:
        Document: The loaded odfdo Document object.
    """
    if input_path:
        document = Document(input_path)
    else:  # pragma: no cover
        detect_stdin_timeout()
        content = io.BytesIO(sys.stdin.buffer.read())
        document = Document(content)
        content.close()
    return document


def save_document(document: Document, output_path: str | None) -> None:
    """Saves an ODF document to a file path or standard output.

    If `output_path` is provided, the document is saved to that file.
    Otherwise, the document is written to the standard output stream.

    Args:
        document: The odfdo Document object to save.
        output_path: The path to the output ODF file.
    """
    if output_path:
        return document.save(output_path)
    with io.BytesIO() as content:
        document.save(content)
        content.seek(0)
        sys.stdout.buffer.write(content.read())
