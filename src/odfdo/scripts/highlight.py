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
"""Command-line script to highlight text in an ODF document.

This script searches for a given regular expression pattern in an ODF text
document and applies a style to the matching text. The style can include
italic, bold, text color, and background color.
"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from itertools import chain

from odfdo import Document, Style, __version__
from odfdo.utils.script_utils import read_document, save_document

PROG = "odfdo-highlight"


def configure_parser() -> ArgumentParser:
    description = (
        "Search for a regular expression pattern in an ODF text document "
        "and apply a highlighting style to the matching text. "
        "The style can include italic, bold, text color, and background color."
    )
    epilog = (
        "This tool is useful for visually emphasizing specific content "
        "within your ODF documents based on search patterns."
    )
    parser = ArgumentParser(prog=PROG, description=description, epilog=epilog)

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
        "-a",
        "--italic",
        action="store_true",
        dest="italic",
        help="use italic font",
    )

    parser.add_argument(
        "-b",
        "--bold",
        action="store_true",
        dest="bold",
        help="use bold font",
    )

    parser.add_argument(
        "-c",
        "--color",
        action="store",
        default="",
        dest="color",
        required=False,
        help="font color",
    )
    parser.add_argument(
        "-g",
        "--background",
        action="store",
        default="",
        dest="background",
        required=False,
        help="font background color",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} v{__version__}",
    )
    parser.add_argument(
        "pattern",
        action="store",
        help="search pattern (regular expression)",
    )
    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def error(message: str) -> str:
    return f"{PROG}: error: {message}"


def check_args(args: Namespace) -> None:
    if not any((args.italic, args.bold, args.color, args.background)):
        raise SystemExit(error("at least some style argument is required"))


def make_style(document: Document, args: Namespace) -> str:
    def _display_name() -> str:
        parts = ["odfdo", "highlight"]
        if args.color:
            parts.append(args.color.lower())
        if args.background:
            parts.append(args.background.lower())
        if args.italic:
            parts.append("italic")
        if args.bold:
            parts.append("bold")
        return " ".join(parts)

    display_name = _display_name()
    name = display_name.replace(" ", "_20_")
    if document.get_style("text", name):
        # style already in the document
        return name

    if args.color:
        color = args.color
    else:
        color = None
    if args.background:
        background = args.background
    else:
        background = None

    style = Style(
        family="text",
        name=name,
        display_name=display_name,
        italic=args.italic,
        bold=args.bold,
        color=color,
        background_color=background,
    )
    document.insert_style(style, automatic=True)
    return name


def apply_style(document: Document, style_name: str, pattern: str) -> None:
    body = document.body
    for paragraph in chain(
        body.get_paragraphs(content=pattern), body.get_headers(content=pattern)
    ):
        if paragraph.parent and paragraph.parent.tag in (
            "text:index-title",
            "text:index-body",
        ):
            continue
        paragraph.set_span(style=style_name, regex=pattern)


def highlight_document(document: Document, args: Namespace) -> None:
    style_name = make_style(document, args)
    apply_style(document, style_name, args.pattern)


def highlight(args: Namespace) -> None:
    document = read_document(args.input_file)
    highlight_document(document, args)
    save_document(document, args.output_file)


def main() -> int:
    args: Namespace = parse_cli_args()
    return main_highlight(args)


def main_highlight(args: Namespace) -> int:
    check_args(args)
    try:
        highlight(args)
    except Exception:
        configure_parser().print_help()
        print()
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
