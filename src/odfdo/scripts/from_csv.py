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
"""Command-line script to import a CSV file into an ODS document.

This script reads data from a CSV file (or standard input) and creates a new
ODF spreadsheet (.ods) containing the data in a table.
"""

from __future__ import annotations

import io
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from odfdo import Document, Table, __version__
from odfdo.utils.script_utils import detect_stdin_timeout, save_document

PROG = "odfdo-from-csv"
STDIN_TIMEOUT = 0.5
DEFAULT_NAME = "table"


def configure_parser() -> ArgumentParser:
    description = (
        "Import data from a CSV file into a new ODS (OpenDocument Spreadsheet) file. "
        "The script reads CSV data and populates a table in the ODS document."
    )
    epilog = (
        "The CSV format detection is handled automatically by the Python CSV module, "
        "providing basic functionality for importing tabular data. "
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
        default=None,
        help="input CSV file, if option not present, read from stdin",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output_file",
        metavar="OUTPUT",
        required=False,
        help="output ODF file, if option not present, write to stdout",
    )

    parser.add_argument(
        "-t",
        "--table",
        action="store",
        dest="table_name",
        metavar="TABLE",
        required=False,
        help=f"table name, if option not present, default to '{DEFAULT_NAME}'",
    )
    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def read_document(input_file: str | None) -> str:
    if input_file:
        csv_content = Path(input_file).read_text()
    else:  # pragma: no cover
        detect_stdin_timeout()
        content = io.BytesIO(sys.stdin.buffer.read())
        csv_content = content.getvalue().decode()
        content.close()
    return csv_content


def from_csv(args: Namespace) -> None:
    csv_content = read_document(args.input_file)
    document = Document("ods")
    table = Table.from_csv(
        content=csv_content,
        name=args.table_name or DEFAULT_NAME,
    )
    document.body.clear()
    document.body.append(table)
    save_document(document, args.output_file)


def main() -> int:
    args: Namespace = parse_cli_args()
    return main_from_csv(args)


def main_from_csv(args: Namespace) -> int:
    try:
        from_csv(args)
    except Exception:
        configure_parser().print_help()
        print()
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
