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
#          Romain Gauthier <romain@itaapy.com>
"""Command-line script to manipulate styles in an ODF document.

This script provides functionalities to show, delete, and merge styles
from one ODF document to another.
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from io import BytesIO
from pathlib import Path

from odfdo import Document, __version__

PROG = "odfdo-styles"


def configure_parser() -> ArgumentParser:
    description = (
        "Manipulate styles within OpenDocument files: display, delete, or merge them."
    )
    epilog = (
        "This tool offers fine-grained control over ODF document styles. "
        "You can inspect automatic or common styles, view their properties, "
        "delete styles (except default ones) to reduce document size, "
        "or merge styles from another ODF file, replacing any with the same name."
    )
    parser = ArgumentParser(prog=PROG, description=description, epilog=epilog)

    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} v{__version__}",
    )
    parser.add_argument(
        "-a",
        "--automatic",
        action="store_true",
        default=False,
        help="show automatic styles only",
    )
    parser.add_argument(
        "-c",
        "--common",
        action="store_true",
        default=False,
        help="show common styles only",
    )
    parser.add_argument(
        "-p",
        "--properties",
        action="store_true",
        help="show properties of styles",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="return a copy with all styles (except default) deleted from <file>",
    )
    parser.add_argument(
        "-m",
        "--merge-styles-from",
        dest="merge",
        metavar="FILE",
        help=(
            "copy styles from FILE to <file>. Any style with the same "
            "name will be replaced."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="dump the output into FILE",
    )
    parser.add_argument(
        "input",
        action="store",
        help="input ODF file",
    )
    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def show_styles(
    document: Document,
    target: str | Path | None = None,
    automatic: bool = True,
    common: bool = True,
    properties: bool = False,
) -> None:
    """Show the different styles of a document and their properties."""
    styles_content = document.show_styles(
        automatic=automatic,
        common=common,
        properties=properties,
    )
    # Print the output
    if target is None:
        print(styles_content, end="")
        return
    Path(target).write_text(styles_content)


def delete_styles(
    document: Document,
    target: str | Path,
    pretty: bool = False,
) -> None:
    number_deleted = document.delete_styles()
    document.save(target=target, pretty=pretty)
    msg = f"{number_deleted} styles removed (0 error, 0 warning)."
    print(msg, file=sys.stderr)
    if isinstance(target, BytesIO):
        sys.stdout.buffer.write(target.getvalue())


# def find_presentation_list_style(body):
#     for frame in body.get_frames(presentation_class="outline"):
#         first_list = frame.get_list()
#         if first_list is not None:
#             return first_list.get_style()
#     return None


def merge_presentation_styles(document: Document, source: Document) -> None:
    # Apply master page found
    raise NotImplementedError("merge_presentation_styles")  # pragma: no cover
    # source_body = source.body
    # first_page = source_body.get_draw_page()
    # master_page_name = first_page.master_page
    # print(master_page_name)
    # first_master_page = document.get_style("master-page", master_page_name)
    # body = document.body

    # for page in body.get_draw_pages():
    #     page.set_style_attribute(first_page.get_style())
    #     page.set_master_page(first_page.get_master_page())
    #     page.set_presentation_page_layout(first_page.get_presentation_page_layout())
    # Adjust layout -- will obviously work only if content is separated from

    # style: use of master pages, layout, etc.
    # for presentation_class in ODF_CLASSES:
    #     first_frame = source_body.get_frame(presentation_class=presentation_class)
    #     if first_frame is None:
    #         continue
    #     # Mimic frame style
    #     position = first_frame.get_position()
    #     size = first_frame.size
    #     style = first_frame.style
    #     presentation_style = first_frame.get_presentation_style()
    #     for page in body.get_draw_pages():
    #         for frame in page.get_frames(presentation_class=presentation_class):
    #             frame.position = position
    #             frame.size = size
    #             frame.set_style_attribute(style)
    #             frame.set_presentation_style(presentation_style)
    #     # Mimic list style (XXX only first level)
    #     if presentation_class == "outline":
    #         list_style = find_presentation_list_style(source_body)
    #         for page in body.get_draw_pages():
    #             for frame in page.get_frames(presentation_class="outline"):
    #                 for lst in frame.get_lists():
    #                     lst.set_style_attribute(list_style)


def merge_styles(
    document: Document,
    from_file: str | Path,
    target: str | Path | None = None,
    pretty: bool = False,
) -> None:
    source = Document(from_file)
    document.delete_styles()
    document.merge_styles_from(source)
    document.save(target=target, pretty=pretty)
    print("Done (0 error, 0 warning).", file=sys.stderr)


def check_target_file(path: str) -> None:
    if Path(path).exists():  # pragma: no cover
        message = f'The path "{path}" exists, overwrite it? [y/n]'
        print(message, file=sys.stderr)
        line = sys.stdin.readline()
        line = line.strip().lower()
        if line != "y":
            print("Operation aborted", file=sys.stderr)
            raise SystemExit(0)


def style_tools(args: Namespace) -> None:
    doc = Document(args.input)

    if args.delete:
        target = args.output
        if target is None:
            msg = (
                "Error: Will not delete in-place: output file needed or '-' for stdout"
            )
            print(msg, file=sys.stderr)
            raise SystemExit(1)
        elif target == "-":
            target = BytesIO()
        else:
            check_target_file(target)
        delete_styles(doc, target)
    elif args.merge:
        merge_styles(doc, args.merge, target=args.output)
    else:
        automatic = args.automatic
        common = args.common
        if not automatic ^ common:
            automatic, common = True, True
        show_styles(
            doc,
            args.output,
            automatic=automatic,
            common=common,
            properties=args.properties,
        )


def main() -> None:
    args: Namespace = parse_cli_args()
    main_styles(args)


def main_styles(args: Namespace) -> None:
    try:
        style_tools(args)
    except Exception as e:
        configure_parser().print_help()
        print()
        print(f"Error: {e.__class__.__name__}, {e}")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
