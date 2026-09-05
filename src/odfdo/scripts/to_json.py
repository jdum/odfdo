# Copyright 2018-2026 Jérôme Dumonteil
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
"""Command-line script to export tables from an ODF document to JSON."""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from odfdo import __version__
from odfdo.utils.script_utils import read_document

PROG = "odfdo-to-json"


def configure_parser() -> ArgumentParser:
    description = (
        "Export one or all tables from an ODF (OpenDocument) spreadsheet or "
        "text file to JSON. The script extracts all tables into a JSON "
        "object mapping table names to 2D lists of cell values."
    )
    epilog = (
        "This tool outputs standard JSON formatted data. "
        "It can output to a file or standard output, with optional "
        "pretty-printing formatting."
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
        default=None,
        help="input ODF file, if option not present, read from stdin",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output_file",
        metavar="OUTPUT",
        required=False,
        help="output JSON file, if option not present, write to stdout",
    )
    parser.add_argument(
        "-t",
        "--table",
        action="store",
        dest="table_name",
        metavar="TABLE",
        required=False,
        help="table name, if option not present, export all tables",
    )
    parser.add_argument(
        "-d",
        "--hidden",
        action="store_true",
        dest="include_hidden",
        default=False,
        help="export hidden tables as well (hidden tables omitted by default)",
    )
    parser.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        default=False,
        help="pretty-print JSON output with indentation",
    )

    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def to_json(args: Namespace) -> None:
    document = read_document(args.input_file)
    if args.table_name:
        table = document.body.get_table_by_name(args.table_name)
        if not table:
            msg = f"Table {args.table_name!r} not found"
            raise ValueError(msg)
        if not args.include_hidden and not document.get_table_displayed(table):
            msg = f"Table {args.table_name!r} is hidden"
            raise ValueError(msg)
        content = table.to_json(path_or_file=args.output_file, pretty=args.pretty)
    else:
        content = document.to_json(
            path_or_file=args.output_file,
            include_hidden=args.include_hidden,
            pretty=args.pretty,
        )

    if content is not None:
        sys.stdout.buffer.write(content.encode())
        sys.stdout.buffer.write(b"\n")


def main() -> int:
    args: Namespace = parse_cli_args()
    return main_to_json(args)


def main_to_json(args: Namespace) -> int:
    try:
        to_json(args)
    except Exception:
        configure_parser().print_help()
        print()
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
