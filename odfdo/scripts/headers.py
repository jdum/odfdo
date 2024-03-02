# Copyright 2018-2024 Jérôme Dumonteil
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
from __future__ import annotations

import io
import selectors
import sys
from argparse import ArgumentParser, Namespace

from odfdo import Document, Header, __version__

PROG = "odfdo-headers"
STDIN_TIMEOUT = 0.5


def configure_parser() -> ArgumentParser:
    description = "Print the headers of the document."
    parser = ArgumentParser(prog=PROG, description=description)
    parser.add_argument(
        "-d",
        "--depth",
        action="store",
        dest="depth",
        type=int,
        default=999,
        required=False,
        help="depth of headers hierarchy to print",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} v{__version__}",
    )
    parser.add_argument(
        "document",
        nargs="?",
        default=None,
        action="store",
        help="input document. if not present, read from stdin",
    )
    return parser


def error(message: str) -> str:
    return f"{PROG}: error: {message}"


def detect_stdin_timeout() -> None:
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin, selectors.EVENT_READ)
    something = selector.select(timeout=STDIN_TIMEOUT)
    if not something:
        raise SystemExit(error("timeout reading from stdin"))
    selector.close()


def read_document(input_path: str | None) -> Document:
    if input_path:
        return Document(input_path)
    detect_stdin_timeout()
    content = io.BytesIO(sys.stdin.buffer.read())
    document = Document(content)
    content.close()
    return document


def header_numbering(
    header: Header,
    level_indexes: dict[int, int],
    depth: int,
) -> str | None:
    level = header.get_attribute_integer("text:outline-level") or 0
    if level is None or level > depth:
        return None
    number = []
    # < level
    for idx in range(1, level):
        index = level_indexes.setdefault(idx, 1)
        number.append(str(index))
    # == level
    index = level_indexes.setdefault(level, 0) + 1
    level_indexes[level] = index
    number.append(str(index))
    # 3. l > level
    for idx in range(level + 1, depth + 1):
        if idx in level_indexes:
            del level_indexes[idx]
    return ".".join(number) + "."


def headers_document(document: Document, depth: int) -> None:
    body = document.body
    level_indexes: dict[int, int] = {}
    for header in body.get_headers():
        number_str = header_numbering(header, level_indexes, depth)
        if number_str is None:
            continue
        print(f"{number_str} {header}")


def headers(args: Namespace) -> None:
    document = read_document(args.document)
    depth = args.depth
    headers_document(document, depth)


def main() -> int:
    parser = configure_parser()
    args = parser.parse_args()
    try:
        headers(args)
    except Exception:
        parser.print_help()
        print()
        raise
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
