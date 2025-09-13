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
from __future__ import annotations

import io
import selectors
import sys
from argparse import ArgumentParser, Namespace

from odfdo import Document, __version__

PROG = "odfdo-to-csv"
STDIN_TIMEOUT = 0.5


def configure_parser() -> ArgumentParser:
    description = "Export a .ods table to a CSV file."
    epilog = "Minimal-featured CSV exporter based on the Python CSV module."
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


def error(message: str) -> str:
    return f"\n{PROG}: {message}"


def detect_stdin_timeout() -> None:
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin, selectors.EVENT_READ)
    something = selector.select(timeout=STDIN_TIMEOUT)
    if not something:
        raise SystemExit(error("timeout reading from stdin"))
    selector.close()


def read_document(input_file: str | None) -> Document:
    if input_file:
        return Document(input_file)
    detect_stdin_timeout()
    content = io.BytesIO(sys.stdin.buffer.read())
    document = Document(content)
    content.close()
    return document


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
        if not table:
            raise ValueError("No table found")
    if args.unix:
        dialect = "unix"
    else:
        dialect = "excel"
    content = table.to_csv(path_or_file=args.output_file, dialect=dialect)
    if content is not None:
        sys.stdout.buffer.write(content.encode())


def main() -> int:
    parser = configure_parser()
    args = parser.parse_args()
    try:
        to_csv(args)
    except Exception:
        parser.print_help()
        print()
        raise
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
