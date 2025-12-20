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
"""Command-line script to show or set user-defined fields in an ODF document.

This script allows for inspecting the values of user-defined fields and
updating them.
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from typing import TYPE_CHECKING

from odfdo import Document, Element, __version__
from odfdo.utils.script_utils import read_document, save_document

if TYPE_CHECKING:
    from odfdo.user_field_declaration import UserFieldDecl

PROG = "odfdo-userfield"


def configure_parser() -> ArgumentParser:
    description = "Inspect and modify user-defined fields within an ODF document."
    epilog = (
        "This tool allows you to view the values of specific user fields, "
        "list all available user fields, and update their values. "
        "User fields are custom data points stored in the document's metadata.\n\n"
        "Examples:\n"
        "  # Show the value of a specific user field named 'city'\n"
        "  $ odfdo-userfield -i file.odt -f city\n\n"
        "  # Show name, type, and value for fields 'city' and 'phone'\n"
        "  $ odfdo-userfield -i file.odt -ntf city phone\n\n"
        "  # Show all user fields with their name and value (repr format)\n"
        "  $ odfdo-userfield -i file.odt -anr\n\n"
        "  # Set the value of 'city' to 'Lyon' and 'phone' to '99 99', saving to result.odt\n"
        "  $ odfdo-userfield -i file.odt -o result.odt -s city Lyon -s phone '99 99'"
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
        help="If setting values, output file. if option not present, write to stdout",
    )
    parser.add_argument(
        "-f",
        "--field",
        action="extend",
        dest="fields",
        required=False,
        nargs=1,
        help="name of field to show",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        required=False,
        help="show all fields",
    )
    parser.add_argument(
        "-n",
        "--name",
        action="store_true",
        required=False,
        help="show field name",
    )
    parser.add_argument(
        "-t",
        "--type",
        action="store_true",
        required=False,
        help="show field type",
    )
    parser.add_argument(
        "-r",
        "--repr",
        action="store_true",
        required=False,
        help="format value using repr()",
    )
    parser.add_argument(
        "-s",
        "--set",
        action="append",
        dest="changes",
        required=False,
        nargs=2,
        help="set field value",
    )
    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def main() -> None:
    args: Namespace = parse_cli_args()
    main_userfields(args)


def main_userfields(args: Namespace) -> None:
    try:
        document_userfields(args)
    except Exception as e:
        configure_parser().print_help()
        print()
        print(f"Error: {e.__class__.__name__}, {e}")
        raise SystemExit(1) from None


def document_userfields(args: Namespace) -> None:
    if args.all or args.fields:
        document = read_document(args.input_file)
        return show_fields(document, args)
    if args.changes:
        document = read_document(args.input_file)
        change_fields(document, args.changes)
        save_document(document, args.output_file)
    else:
        raise ValueError("missing arguments")


def _field_string(field: UserFieldDecl, args: Namespace) -> str:
    value, tpe = field.get_value(get_type=True)
    if args.repr:
        repr_value = repr(value)
    else:
        repr_value = str(value)
    line = []
    if args.name:
        line.append(f"{field.name}")
    if args.type:
        line.append(f"({tpe})")
    if line:
        return " ".join(line) + f": {repr_value}"
    return repr_value


def show_fields(document: Document, args: Namespace) -> None:
    field_set = set()
    if not args.all and args.fields:
        field_set = set(args.fields)
    body = document.body
    if hasattr(body, "get_user_field_decl_list"):
        for field in body.get_user_field_decl_list():
            if not args.all and field.name not in field_set:
                continue
            print(_field_string(field, args))
    else:  # pragma: nocover
        print("Warning: Document can not have user fields", file=sys.stderr)


def _change_field(body: Element, name: str, value: str) -> None:
    field = body.get_user_field_decl(name)  # type: ignore[attr-defined]
    if not field:
        print(f"Warning: unknown user-field {name!r}", file=sys.stderr)
        return
    field.set_value(value)


def change_fields(document: Document, changes: list[list[str]]) -> None:
    body = document.body
    if hasattr(body, "get_user_field_decl"):
        for name_value in changes:
            _change_field(body, name_value[0], name_value[1])
    else:  # pragma: nocover
        print("Warning: Document can not have user fields", file=sys.stderr)


if __name__ == "__main__":
    main()
