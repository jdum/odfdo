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
"""Command-line script to display the headers of an ODF document.

This script reads an ODF text document and prints its headers, optionally
up to a specified depth, with hierarchical numbering.
"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace

from odfdo import Document, Header, __version__
from odfdo.utils.script_utils import read_document

PROG = "odfdo-headers"


def configure_parser() -> ArgumentParser:
    description = (
        "Display the hierarchical headers (headings) of an ODF text document. "
        "The headers are printed with their numbering and can be limited "
        "by a specified depth."
    )
    epilog = (
        "This tool is useful for quickly outlining the structure of a document "
        "or verifying its logical organization."
    )
    parser = ArgumentParser(prog=PROG, description=description, epilog=epilog)
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


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def header_numbering(
    header: Header,
    level_indexes: dict[int, int],
    depth: int,
) -> str | None:
    level = header.get_attribute_integer("text:outline-level") or 0
    if level is None or level > depth:
        return None
    numbers: list[int] = []
    # before hedaer level
    for idx in range(1, level):
        numbers.append(level_indexes.setdefault(idx, 1))
    # header level
    index = level_indexes.get(level, 0) + 1
    level_indexes[level] = index
    numbers.append(index)
    # after header level
    idx = level + 1
    while idx in level_indexes:
        del level_indexes[idx]
        idx += 1
    return ".".join(str(x) for x in numbers) + "."


def headers_document(document: Document, depth: int) -> None:
    body = document.body
    level_indexes: dict[int, int] = {}
    for header in body.headers:
        number_str = header_numbering(header, level_indexes, depth)
        if number_str is None:
            continue
        print(f"{number_str} {header}", end="")


def headers(args: Namespace) -> None:
    document = read_document(args.document)
    depth = args.depth
    headers_document(document, depth)


def main() -> int:
    args: Namespace = parse_cli_args()
    return main_headers(args)


def main_headers(args: Namespace) -> int:
    try:
        headers(args)
    except Exception:
        configure_parser().print_help()
        print()
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
