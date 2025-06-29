# Copyright 2018-2025 Jérôme Dumonteil
# Copyright (c) 2009-2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
# Authors: Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from shutil import rmtree

from odfdo import Document, __version__

PROG = "odfdo-show"


def configure_parser() -> ArgumentParser:
    description = description = (
        "Dump text from an OpenDocument file to the standard "
        "output, optionally styles and meta (and the Pictures/* "
        'in "-o <DIR>" mode)'
    )
    parser = ArgumentParser(prog=PROG, description=description)

    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} v{__version__}",
    )
    parser.add_argument(
        "-m",
        "--meta",
        action="store_true",
        default=False,
        help="dump metadata to stdout",
    )
    parser.add_argument(
        "-s",
        "--styles",
        action="store_true",
        default=False,
        help="dump styles to stdout",
    )
    parser.add_argument(
        "-n",
        "--no-content",
        action="store_true",
        default=False,
        help="do not dump content to stdout",
    )
    parser.add_argument(
        "-r",
        "--rst",
        action="store_true",
        default=False,
        help="dump the content file with a reST syntax",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        help="dump the output into DIR",
    )
    parser.add_argument(
        "input",
        action="store",
        help="input ODF file to show",
    )
    return parser


def clean_filename(name: str) -> str:
    allowed_characters = {".", "-", "@"}
    result = []
    for char in name:
        if char in allowed_characters or char.isalnum():
            result.append(char)
        else:
            result.append("\t")
    return "_".join("".join(result).split())


def dump_pictures(document: Document, target: str | Path) -> None:
    for part_name in document.parts:
        if not part_name.startswith("Pictures/"):
            continue
        path = Path(target, "Pictures")
        if not path.exists():
            path.mkdir(parents=False, exist_ok=False)
        data = document.get_part(part_name)
        path = Path(target, part_name)
        path.write_bytes(data)  # type: ignore


def spreadsheet_to_stdout(document: Document) -> None:
    body = document.body
    for table in body.tables:
        table.rstrip(aggressive=True)
        print(table.to_csv(None))


def spreadsheet_to_csv(document: Document, output: Path) -> None:
    body = document.body
    for table in body.tables:
        name = table.name
        filename = clean_filename(name) + ".csv"
        print(filename)
        table.rstrip(aggressive=True)
        table.to_csv(output / filename)


def print_format_error(doc_type: str) -> None:
    msg = f"Error: The OpenDocument format '{doc_type}' is not supported yet."
    print(msg, file=sys.stderr)


def check_target_directory(path: Path) -> None:
    if path.exists():
        message = f'The path "{path}" exists, overwrite it? [y/n]'
        print(message, file=sys.stderr)
        line = sys.stdin.readline()
        line = line.strip().lower()
        if line != "y":
            print("Operation aborted", file=sys.stderr)
            raise SystemExit(0)


def show_output(
    args: Namespace,
    doc: Document,
    doc_type: str,
) -> None:
    output = Path(args.output)
    check_target_directory(output)
    if output.exists():
        rmtree(output)  # pragma: no cover
    output.mkdir(parents=True, exist_ok=True)
    (output / "meta.txt").write_text(doc.get_formated_meta())
    (output / "styles.txt").write_text(doc.show_styles())
    dump_pictures(doc, output)

    if doc_type in {"text", "text-template", "presentation", "presentation-template"}:
        (output / "content.rst").write_text(doc.get_formatted_text(rst_mode=args.rst))
    elif doc_type in {"spreadsheet", "spreadsheet-template"}:
        spreadsheet_to_csv(doc, output)
    else:
        print_format_error(doc_type)
        raise SystemExit(1)


def show(args: Namespace) -> None:
    doc = Document(args.input)
    doc_type = doc.get_type()

    if args.output:
        return show_output(args, doc, doc_type)
    if args.meta:
        print(doc.get_formated_meta())
    if args.styles:
        print(doc.show_styles())
    if doc_type in {"text", "text-template", "presentation", "presentation-template"}:
        if not args.no_content:
            print(doc.get_formatted_text(rst_mode=args.rst))
    elif doc_type in {"spreadsheet", "spreadsheet-template"}:
        if not args.no_content:
            spreadsheet_to_stdout(doc)
    else:
        print_format_error(doc_type)
        raise SystemExit(1)


def main() -> None:
    parser = configure_parser()
    args = parser.parse_args()
    try:
        show(args)
    except Exception as e:
        parser.print_help()
        print()
        print(f"Error: {e.__class__.__name__}, {e}")
        raise SystemExit(1) from None


if __name__ == "__main__":  # pragma: no cover
    main()
