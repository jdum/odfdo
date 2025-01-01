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
from argparse import ArgumentParser

from odfdo import Document, __version__

PROG = "odfdo-table-shrink"
STDIN_TIMEOUT = 0.5


def configure_parser() -> ArgumentParser:
    description = "Shrink tables to optimize width and height (experimental)."
    parser = ArgumentParser(prog=PROG, description=description)

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
    return parser


def main() -> None:
    parser = configure_parser()
    args = parser.parse_args()

    try:
        shrink_tables(
            args.input_file,
            args.output_file,
        )
    except Exception as e:
        parser.print_help()
        print()
        print(f"Error: {e.__class__.__name__}, {e}")
        raise SystemExit(1) from None


def detect_stdin_timeout() -> None:
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin, selectors.EVENT_READ)
    something = selector.select(timeout=STDIN_TIMEOUT)
    if not something:
        raise ValueError("Timeout reading from stdin")
    selector.close()


def read_document(input_path: str | None) -> Document:
    if input_path:
        return Document(input_path)
    detect_stdin_timeout()
    content = io.BytesIO(sys.stdin.buffer.read())
    document = Document(content)
    content.close()
    return document


def save_document(document: Document, output_path: str | None) -> None:
    if output_path:
        return document.save(output_path)
    with io.BytesIO() as content:
        document.save(content)
        content.seek(0)
        sys.stdout.buffer.write(content.read())


def shrink_tables(
    input_path: str | None,
    output_path: str | None,
) -> None:
    document = read_document(input_path)
    if document.get_type() not in {"spreadsheet", "spreadsheet-template"}:
        raise TypeError("Document must be a Spreadsheet type.")
    for table in document.body.tables:
        table.optimize_width()  # type: ignore
    save_document(document, output_path)


if __name__ == "__main__":  # pragma: no cover
    main()
