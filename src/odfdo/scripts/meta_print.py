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
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent

from odfdo import Document, __version__

PROG = "odfdo-meta-print"
STDIN_TIMEOUT = 0.5


def configure_parser() -> ArgumentParser:
    description = dedent(
        "Print the metadata of an ODF file.\n\n"
        "By default, populated metadata is printed as text "
        "(optional: with the ODF version and default style language).\n"
        "With the -j option, export all metadata fields in JSON "
        "format, including empty fields.\n"
    )

    parser = ArgumentParser(
        prog=PROG,
        description=description,
        formatter_class=RawTextHelpFormatter,
    )

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
        help="output file (for text or json). if option not present, write to stdout",
    )
    parser.add_argument(
        "-v",
        "--odf-version",
        action="store_true",
        required=False,
        help="show OpenDocument Format version (not a meta field)",
    )
    parser.add_argument(
        "-l",
        "--language",
        action="store_true",
        required=False,
        help="show language from document style (not a meta field)",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        required=False,
        help="export full metadata as json",
    )
    return parser


def main() -> None:
    parser = configure_parser()
    args = parser.parse_args()
    try:
        print_meta_fields(args)
    except Exception as e:
        parser.print_help()
        print()
        print(f"Error: {e.__class__.__name__}, {e}")
        raise SystemExit(1)


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


def print_meta_fields(args: Namespace) -> None:
    document = read_document(args.input_file)
    print_doc_fields(document, args)


def print_doc_fields(document: Document, args: Namespace) -> None:
    if args.json:
        print_json(document, args)
    else:
        print_text(document, args)


def save_content(content: str, args: Namespace, encoding: str = "utf8") -> None:
    if args.output_file:
        Path(args.output_file).write_text(content.strip() + "\n", encoding=encoding)
    else:
        print(content.strip())


def print_json(document: Document, args: Namespace) -> None:
    content = document.meta.as_json(full=True)
    save_content(content, args, "utf8")


def print_text(document: Document, args: Namespace) -> None:
    blocks: list[str] = []
    meta = document.meta
    if args.odf_version:
        blocks.append(f"OpenDocument format version: {meta.odf_office_version}")
    if args.language:
        blocks.append(f"Default style language: {document.language}")
    blocks.append(meta.as_text(no_user_defined_msg="None"))
    save_content("\n".join(blocks), args)


if __name__ == "__main__":  # pragma: no cover
    main()
