# Copyright 2018-2024 Jérôme Dumonteil
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
from optparse import OptionParser

from odfdo import Document, __version__

STDIN_TIMEOUT = 0.5


def configure_parser() -> OptionParser:
    usage = "%prog [-i <file in>] [-o <file out>] pattern replacement"
    description = "Search and replace text in ODF file using regex pattern"
    parser = OptionParser(usage, version=__version__, description=description)

    parser.add_option(
        "-i",
        "--input",
        action="store",
        type="string",
        dest="input_file",
        nargs=1,
        help="input file. if option not present, read from stdin.",
    )

    parser.add_option(
        "-o",
        "--output",
        action="store",
        type="string",
        dest="output_file",
        nargs=1,
        help="output file. if option not present, write to stdout.",
    )
    return parser


def main() -> None:
    parser = configure_parser()
    options, args = parser.parse_args()

    if len(args) != 2:
        parser.print_help()
        print("Two arguments are required (pattern, replacement).")
        raise SystemExit(1)

    try:
        search_replace(args[0], args[1], options.input_file, options.output_file)
    except Exception:
        parser.print_help()
        print()
        raise


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


def search_replace(
    pattern: str,
    replacement: str,
    input_path: str | None,
    output_path: str | None,
) -> None:
    document = read_document(input_path)
    body = document.body
    body.replace(pattern, replacement)
    save_document(document, output_path)


if __name__ == "__main__":  # pragma: no cover
    main()
