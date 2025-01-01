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
from __future__ import annotations

from argparse import ArgumentParser
from difflib import ndiff, unified_diff
from os import stat
from time import ctime

from odfdo import Document, __version__

PROG = "odfdo-diff"


def configure_parser() -> ArgumentParser:
    description = "Show a diff between two .odt files."
    parser = ArgumentParser(prog=PROG, description=description)
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


def main() -> None:
    parser = configure_parser()
    args = parser.parse_args()

    try:
        print_diff(args.document1, args.document2, args.ndiff)
    except Exception as e:
        parser.print_help()
        print()
        print(f"Error: {e}")
        raise SystemExit(1) from None


def print_diff(path0: str, path1: str, ndiff: bool) -> None:
    # Open the 2 documents, diff only for ODT
    doc0 = Document(path0)
    doc1 = Document(path1)
    if doc0.get_type() != "text" or doc1.get_type() != "text":
        raise ValueError(f"{PROG} requires input documents of type text")
    if ndiff:
        print(make_ndiff(doc0, doc1))
    else:
        print(make_diff(doc0, doc1, path0, path1))


def make_ndiff(doc0: Document, doc1: Document) -> str:
    # Convert in text before the diff
    text0 = doc0.get_formatted_text(True).splitlines(True)
    text1 = doc1.get_formatted_text(True).splitlines(True)
    # Make the diff !
    return "".join(ndiff(text0, text1, None, None))


def make_diff(doc0: Document, doc1: Document, path0: str, path1: str) -> str:
    # Convert in text before the diff
    text0 = doc0.get_formatted_text(True).splitlines(True)
    text1 = doc1.get_formatted_text(True).splitlines(True)
    # Make the diff !
    fromdate = ctime(stat(path0).st_mtime)
    todate = ctime(stat(path1).st_mtime)
    return "".join(unified_diff(text0, text1, path0, path1, fromdate, todate))


if __name__ == "__main__":  # pragma: no cover
    main()
