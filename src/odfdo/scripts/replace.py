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
"""Command-line script to search and replace text in an ODF document.

This script finds all occurrences of a given regular expression pattern in an
ODF document and replaces them with a specified string.
"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace

from odfdo import __version__
from odfdo.utils.script_utils import read_document, save_document

PROG = "odfdo-replace"


def configure_parser() -> ArgumentParser:
    description = (
        "Find and replace text in an ODF file using a regular expression pattern."
    )
    epilog = (
        "This tool supports standard regular expressions for pattern matching. "
        "Replacements can be made with or without preserving original formatting. "
        "Input can be from a specified file or standard input. "
        "Output can be to a specified file or standard output."
    )
    parser = ArgumentParser(prog=PROG, description=description, epilog=epilog)

    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} v{__version__}",
    )
    parser.add_argument(
        "-i",
        "--input",
        action="store",
        dest="input_file",
        metavar="INPUT",
        required=False,
        help="input file. if option not present, read from stdin",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output_file",
        metavar="OUTPUT",
        required=False,
        help="output file. if option not present, write to stdout",
    )
    parser.add_argument(
        "-f",
        "--formatted",
        action="store_true",
        default=False,
        help="keep replacement string format",
    )
    parser.add_argument(
        "pattern",
        action="store",
        help="search pattern (regular expression)",
    )
    parser.add_argument(
        "replacement",
        action="store",
        help="replacement text",
    )
    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def main() -> None:
    args: Namespace = parse_cli_args()
    main_replace(args)


def main_replace(args: Namespace) -> None:
    try:
        search_replace(
            args.pattern,
            args.replacement,
            args.input_file,
            args.output_file,
            args.formatted,
        )
    except Exception as e:
        configure_parser().print_help()
        print()
        print(f"Error: {e.__class__.__name__}, {e}")
        raise SystemExit(1) from None


def search_replace(
    pattern: str,
    replacement: str,
    input_path: str | None,
    output_path: str | None,
    formatted: bool = False,
) -> None:
    document = read_document(input_path)
    body = document.body
    body.replace(pattern, replacement, formatted)
    save_document(document, output_path)


if __name__ == "__main__":
    main()
