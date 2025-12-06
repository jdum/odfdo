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
# Authors: David Versmisse <david.versmisse@itaapy.com>
"""Command-line script to show the differences between two ODT files.

This script compares the textual content of two ODT documents and displays
the differences in either a standard unified diff format or an ndiff format.
"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from difflib import ndiff, unified_diff
from os import stat
from time import ctime

from odfdo import Document, __version__

PROG = "odfdo-diff"


def configure_parser() -> ArgumentParser:
    description = (
        "Show a diff between the textual content of two ODT files. "
        "By default, the output is in the unified diff format."
    )
    epilog = (
        "This tool is useful for comparing two versions of a document "
        "and tracking changes in its textual content."
    )
    parser = ArgumentParser(prog=PROG, description=description, epilog=epilog)
    parser.add_argument(
        "-n",
        "--ndiff",
        default=False,
        action="store_true",
        help='use a contextual "ndiff" format to display the output',
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} v{__version__}",
    )
    parser.add_argument(
        "document1",
        action="store",
        help="first input document",
    )
    parser.add_argument(
        "document2",
        action="store",
        help="second input document",
    )
    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def main() -> None:
    args: Namespace = parse_cli_args()
    main_diff(args)


def main_diff(args: Namespace) -> None:
    try:
        print_diff(args)
    except Exception as e:
        configure_parser().print_help()
        print()
        print(f"Error: {e}")
        raise SystemExit(1) from None


def print_diff(args: Namespace) -> None:
    # Open the 2 documents, diff only for ODT
    doc1 = Document(args.document1)
    doc2 = Document(args.document2)
    if doc1.get_type() != "text" or doc2.get_type() != "text":
        raise ValueError(f"{PROG} requires input documents of type text")
    if args.ndiff:
        print(make_ndiff(doc1, doc2))
    else:
        print(make_diff(doc1, doc2, args.document1, args.document2))


def make_ndiff(doc1: Document, doc2: Document) -> str:
    # Convert in text before the diff
    text1 = doc1.get_formatted_text(True).splitlines(True)
    text2 = doc2.get_formatted_text(True).splitlines(True)
    # Make the diff !
    return "".join(ndiff(text1, text2, None, None))


def make_diff(doc1: Document, doc2: Document, path1: str, path2: str) -> str:
    # Convert in text before the diff
    text1 = doc1.get_formatted_text(True).splitlines(True)
    text2 = doc2.get_formatted_text(True).splitlines(True)
    # Make the diff !
    fromdate = ctime(stat(path1).st_mtime)
    todate = ctime(stat(path2).st_mtime)
    return "".join(unified_diff(text1, text2, path1, path2, fromdate, todate))


if __name__ == "__main__":
    main()
