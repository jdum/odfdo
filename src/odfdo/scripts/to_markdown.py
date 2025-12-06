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
"""Command-line script to convert an ODF text document to Markdown.

This script reads an ODF text document and prints its content to standard
output in Markdown format.
"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace

from odfdo import __version__
from odfdo.utils.script_utils import read_document

PROG = "odfdo-markdown"


def configure_parser() -> ArgumentParser:
    description = (
        "Convert an ODF text document to Markdown format and print to standard output."
    )
    epilog = (
        "This tool is useful for extracting the textual content of an ODF "
        "document in a lightweight, human-readable, and version-control-friendly "
        "format. It processes the document's main body content."
    )
    parser = ArgumentParser(prog=PROG, description=description, epilog=epilog)
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


def to_md(args: Namespace) -> None:
    document = read_document(args.document)
    print(document.to_markdown())


def main() -> int:
    args: Namespace = parse_cli_args()
    return main_to_md(args)


def main_to_md(args: Namespace) -> int:
    try:
        to_md(args)
    except Exception:
        configure_parser().print_help()
        print()
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
