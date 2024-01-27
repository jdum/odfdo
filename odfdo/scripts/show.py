# Copyright 2018-2024 Jérôme Dumonteil
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

from optparse import OptionParser, Values
from pathlib import Path
from shutil import rmtree

from odfdo import Document, __version__
from odfdo.scriptutils import add_option_output, check_target_directory, printerr


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
    for part_name in document.get_parts():
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
    for table in body.get_tables():
        table.rstrip(aggressive=True)  # type: ignore
        print(table.to_csv(None))  # type: ignore


def spreadsheet_to_csv(document: Document, output: Path) -> None:
    body = document.body
    for table in body.get_tables():
        name = table.name  # type: ignore
        filename = clean_filename(name) + ".csv"
        print(filename)
        table.rstrip(aggressive=True)  # type: ignore
        table.to_csv(output / filename)  # type: ignore


def show_output(
    container_url: str,
    options: Values,
    doc: Document,
    doc_type: str,
) -> None:
    output = Path(options.output)
    check_target_directory(str(output))
    if output.exists():
        rmtree(output)  # pragma: no cover
    output.mkdir(parents=True, exist_ok=True)
    (output / "meta.txt").write_text(doc.get_formated_meta())
    (output / "styles.txt").write_text(doc.show_styles())
    dump_pictures(doc, output)

    if doc_type in {"text", "text-template", "presentation", "presentation-template"}:
        (output / "content.rst").write_text(
            doc.get_formatted_text(rst_mode=options.rst)
        )
    elif doc_type in {"spreadsheet", "spreadsheet-template"}:
        print(doc)
        print(doc.path)
        print(doc.body)
        spreadsheet_to_csv(doc, output)
    else:
        printerr(f"The OpenDocument format '{doc_type}' is not supported yet.")
        raise SystemExit(1)


def show(container_url: str, options: Values) -> None:
    try:
        doc = Document(container_url)
    except Exception as e:
        print(repr(e))
        raise SystemExit(1) from None
    doc_type = doc.get_type()
    # Test it! XXX for TEXT only
    # if doc_type == 'text':
    #    result = test_document(document)
    #    if result is not True:
    #        print('This file is malformed: %s' % result)
    #        print('Please use lpod-clean.py to fix it')
    #        exit(1)
    if options.output:
        return show_output(container_url, options, doc, doc_type)
    if options.meta:
        print(doc.get_formated_meta())
    if options.styles:
        print(doc.show_styles())
    if doc_type in {"text", "text-template", "presentation", "presentation-template"}:
        if not options.no_content:
            print(doc.get_formatted_text(rst_mode=options.rst))
    elif doc_type in {"spreadsheet", "spreadsheet-template"}:
        if not options.no_content:
            spreadsheet_to_stdout(doc)
    else:
        printerr(f"The OpenDocument format '{doc_type}' is not supported yet.")
        raise SystemExit(1)


def main() -> None:
    # Options initialisation
    usage = (
        "%prog [--styles] [--meta] [--no-content] [--rst] <file>\n"
        "       %prog -o <DIR> [--rst] <file>"
    )
    description = (
        "Dump text from an OpenDocument file to the standard "
        "output, optionally styles and meta (and the Pictures/* "
        'in "-o <DIR>" mode)'
    )
    parser = OptionParser(usage, version=__version__, description=description)
    # --meta
    parser.add_option(
        "-m",
        "--meta",
        action="store_true",
        default=False,
        help="dump metadata to stdout",
    )
    # --styles
    parser.add_option(
        "-s",
        "--styles",
        action="store_true",
        default=False,
        help="dump styles to stdout",
    )
    # --no-content
    parser.add_option(
        "-n",
        "--no-content",
        action="store_true",
        default=False,
        help="do not dump content to stdout",
    )
    # --rst
    parser.add_option(
        "-r",
        "--rst",
        action="store_true",
        default=False,
        help="Dump the content file with a reST syntax",
    )
    # --output
    add_option_output(parser, metavar="DIR")
    # Parse !
    options, args = parser.parse_args()
    # Container
    if len(args) != 1:
        parser.print_help()
        raise SystemExit(1)
    container_url = args[0]
    show(container_url, options)


if __name__ == "__main__":  # pragma: no cover
    main()
