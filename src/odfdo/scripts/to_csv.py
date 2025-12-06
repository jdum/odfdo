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
"""Command-line script to export a table from an ODF spreadsheet to CSV.

This script extracts a specified table (or the first table by default) from
an ODS file and converts it to a CSV format, outputting to a file or
standard output.
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace

from odfdo import __version__
from odfdo.utils.script_utils import read_document

PROG = "odfdo-to-csv"


def configure_parser() -> ArgumentParser:
    description = (
        "Export a table from an ODS (OpenDocument Spreadsheet) file to a CSV file. "
        "The script extracts a specified table (or the first table by default) "
        "and converts its content into CSV format."
    )
    epilog = (
        "This tool provides a basic CSV exporter, leveraging the Python CSV module's "
        "functionality. It can output to a file or standard output. "
        "You can choose between 'excel' (default) or 'unix' CSV dialects."
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
        help="input .ods file if option not present, read from stdin",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output_file",
        metavar="OUTPUT",
        required=False,
        help="output CSV file, if option not present, write to stdout",
    )

    parser.add_argument(
        "-t",
        "--table",
        action="store",
        dest="table_name",
        metavar="TABLE",
        required=False,
        help="table name, if option not present, default to the first table",
    )

    parser.add_argument(
        "-u",
        "--unix",
        action="store_true",
        default=False,
        help="use 'unix' dialect for CSV format, default is 'excel'",
    )
    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def to_csv(args: Namespace) -> None:
    document = read_document(args.input_file)
    if document.get_type() not in {"spreadsheet", "spreadsheet-template"}:
        raise TypeError("Document must be a Spreadsheet type.")
    if args.table_name:
        table = document.body.get_table(name=args.table_name)
        if not table:
            raise ValueError(f"Table {args.table_name!r} not found")
    else:
        table = document.body.get_table()
        if not table:  # pragma: no cover
            raise ValueError("No table found")
    if args.unix:
        dialect = "unix"
    else:
        dialect = "excel"
    content = table.to_csv(path_or_file=args.output_file, dialect=dialect)
    if content is not None:  # pragma: no cover
        sys.stdout.buffer.write(content.encode())


def main() -> int:
    args: Namespace = parse_cli_args()
    return main_to_csv(args)


def main_to_csv(args: Namespace) -> int:
    try:
        to_csv(args)
    except Exception:
        configure_parser().print_help()
        print()
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
