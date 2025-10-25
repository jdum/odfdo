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
import json
import selectors
import sys
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent
from typing import Any

from odfdo import Document, __version__

PROG = "odfdo-meta-update"
STDIN_TIMEOUT = 0.5


def configure_parser() -> ArgumentParser:
    description = dedent(
        "Update the metadata of an ODF file.\n\n"
        "With the -j argument: set the metadata from a JSON file "
        "(use odfdo-meta-print -j to see the required JSON format).\n"
        "The loaded metadata are merged with the existing metadata.\n"
        "If the new value of a key is None:\n"
        "  - meta:creation-date: use current time,\n"
        "  - dc:date: use creation date,\n"
        "  - meta:editing-duration: set to zero,\n"
        "  - meta:editing-cycles: set to 1,\n"
        "  - meta:generator: use odfdo generator string.\n"
        "Other keys (not mandatory keys): remove key/value pair from metadata.\n"
        "All user defined metadata are removed.\n\n"
        "With the -s argument: strip metadata to their minimal content.\n"
        "The new metadata values are:\n"
        "  - meta:creation-date: use current time,\n"
        "  - dc:date: use creation date,\n"
        "  - meta:editing-duration: set to zero,\n"
        "  - meta:editing-cycles: set to 1,\n"
        "  - meta:generator: use odfdo generator string,\n"
        "  - all meta:document-statistic values to 0."
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
        help="output file. if option not present, write to stdout",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store",
        dest="json_filename",
        required=False,
        help="input JSON file with replacement metadata",
    )
    parser.add_argument(
        "-s",
        "--strip",
        action="store_true",
        required=False,
        help="strip metadata to their minimal content",
    )
    return parser


def main() -> None:
    parser = configure_parser()
    args = parser.parse_args()
    try:
        update_meta_fields(args)
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


def save_document(document: Document, output_path: str | None) -> None:
    if output_path:
        return document.save(output_path)
    with io.BytesIO() as content:
        document.save(content)
        content.seek(0)
        sys.stdout.buffer.write(content.read())


def update_meta_fields(args: Namespace) -> None:
    document = read_document(args.input_file)
    update_doc_meta_fields(document, args)
    save_document(document, args.output_file)


def update_doc_meta_fields(document: Document, args: Namespace) -> None:
    if args.strip:
        strip_metadata(document)
    elif args.json_filename:
        load_json_metadata(document, args.json_filename)
    else:
        msg = "Either -s or -j option is required"
        raise RuntimeError(msg)


def strip_metadata(document: Document) -> None:
    document.meta.strip()


def load_json_metadata(document: Document, json_filename: str) -> None:
    json_string = Path(json_filename).read_text(encoding="utf-8")
    metadata: dict[str, Any] = json.loads(json_string)
    document.meta.from_dict(metadata)


if __name__ == "__main__":  # pragma: no cover
    main()
