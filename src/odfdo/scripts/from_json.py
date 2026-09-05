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
"""Command-line script to create an ODS document from JSON data."""

from __future__ import annotations

import io
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from odfdo import Document, __version__
from odfdo.utils.script_utils import detect_stdin_timeout, save_document

PROG = "odfdo-from-json"
STDIN_TIMEOUT = 0.5
DEFAULT_NAME = "Table"


def configure_parser() -> ArgumentParser:
    description = (
        "Create an ODS document (OpenDocument Spreadsheet) file. "
        "The script reads JSON data (mapping table names to 2D lists, "
        "or a single 2D list) and populates tables in the ODS document."
    )
    epilog = (
        "Input can be a JSON object mapping table names to 2D lists of cell "
        "values, or a 2D list of row values. Input can be from a specified "
        "file or standard input. Output can be to a specified file or "
        "standard output."
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
        help="input JSON file, if option not present, read from stdin",
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
        help=f"table name when input data is a list, default to '{DEFAULT_NAME}'",
    )
    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def read_json_content(input_file: str | None) -> str:
    if input_file:
        return Path(input_file).read_text(encoding="utf-8")
    detect_stdin_timeout()  # pragma: no cover
    content = io.BytesIO(sys.stdin.buffer.read())
    json_str = content.getvalue().decode("utf-8")
    content.close()
    return json_str


def from_json(args: Namespace) -> None:
    json_content = read_json_content(args.input_file)
    document = Document.from_json(json_content, args.table_name or DEFAULT_NAME)
    save_document(document, args.output_file)


def main() -> int:
    args: Namespace = parse_cli_args()
    return main_from_json(args)


def main_from_json(args: Namespace) -> int:
    try:
        from_json(args)
    except Exception:
        configure_parser().print_help()
        print()
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
