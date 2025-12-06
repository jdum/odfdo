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
"""Command-line script to update the metadata of an ODF document.

This script allows for updating the metadata of an ODF file in two ways:
- From a JSON file: Merges the provided metadata with the existing one.
- Stripping: Resets the metadata to a minimal set of values.
"""

from __future__ import annotations

import json
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent
from typing import Any

from odfdo import Document, __version__
from odfdo.utils.script_utils import read_document, save_document

PROG = "odfdo-meta-update"


def configure_parser() -> ArgumentParser:
    description = (
        "Update the metadata of an ODF file by merging from a JSON file "
        "or stripping to minimal content."
    )
    epilog = dedent(
        "Using the -j option: \n"
        "  - Metadata fields are loaded from a JSON file (see 'odfdo-meta-print -j' for format).\n"
        "  - Loaded metadata is merged with existing metadata.\n"
        "  - Special handling for 'None' values:\n"
        "      - 'meta:creation-date': sets to current time.\n"
        "      - 'dc:date': sets to creation date.\n"
        "      - 'meta:editing-duration': sets to zero.\n"
        "      - 'meta:editing-cycles': sets to 1.\n"
        "      - 'meta:generator': sets to 'odfdo' generator string.\n"
        "  - Other keys with 'None' values are removed.\n"
        "  - All user-defined metadata is removed.\n\n"
        "Using the -s option (strip metadata):\n"
        "  - Resets metadata to minimal content:\n"
        "      - 'meta:creation-date': current time.\n"
        "      - 'dc:date': creation date.\n"
        "      - 'meta:editing-duration': zero.\n"
        "      - 'meta:editing-cycles': 1.\n"
        "      - 'meta:generator': 'odfdo' generator string.\n"
        "      - All 'meta:document-statistic' values set to 0."
    )

    parser = ArgumentParser(
        prog=PROG,
        description=description,
        epilog=epilog,
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


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def main() -> None:
    args: Namespace = parse_cli_args()
    main_meta_update(args)


def main_meta_update(args: Namespace) -> None:
    try:
        update_meta_fields(args)
    except Exception as e:
        configure_parser().print_help()
        print()
        print(f"Error: {e.__class__.__name__}, {e}")
        raise SystemExit(1)


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


if __name__ == "__main__":
    main()
