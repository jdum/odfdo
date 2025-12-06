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
"""Command-line script to print the metadata of an ODF document.

This script extracts and displays the metadata from an ODF file. It can output
the metadata in a human-readable text format or as a JSON object for
programmatic use.
"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent

from odfdo import Document, __version__
from odfdo.utils.script_utils import read_document

PROG = "odfdo-meta-print"


def configure_parser() -> ArgumentParser:
    description = "Extract and display the metadata from an ODF file."
    epilog = dedent(
        "By default, populated metadata fields are printed in a human-readable text format. "
        "Use options to include the ODF version and default style language, "
        "or to export all metadata fields (including empty ones) as a JSON object.\n\n"
        "Examples:\n"
        "  odfdo-meta-print -i document.odt\n"
        "  odfdo-meta-print -i document.odt -v -l\n"
        "  odfdo-meta-print -i document.odt -j > metadata.json"
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


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def main() -> None:
    args: Namespace = parse_cli_args()
    main_meta_print(args)


def main_meta_print(args: Namespace) -> None:
    try:
        print_meta_fields(args)
    except Exception as e:
        configure_parser().print_help()
        print()
        print(f"Error: {e.__class__.__name__}, {e}")
        raise SystemExit(1)


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


if __name__ == "__main__":
    main()
