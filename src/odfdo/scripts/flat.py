# Copyright 2018-2026 Jérôme Dumonteil
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
"""Command-line script to convert ODF files to/from flat XML format.

This script allows for converting a standard ODF file (which is a zip archive)
or a folder structure into a flat ODF XML file (plain XML format), and vice-versa.
This is useful for version control, manual inspection, and text processing of
ODF documents.
"""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path

from odfdo import Document, __version__
from odfdo.const import XML, ZIP

PROG = "odfdo-flat"

FLAT_EXT_MAP: dict[str, str] = {
    ".fodt": ".odt",
    ".fods": ".ods",
    ".fodp": ".odp",
    ".fodg": ".odg",
    ".fodc": ".odc",
    ".fodi": ".odi",
    ".fodf": ".odf",
}


def configure_parser() -> ArgumentParser:
    description = (
        "Convert a standard ODF file (zip archive) or folder structure "
        "to a flat ODF XML file, or convert a flat XML file back to an ODF file."
    )
    epilog = (
        "This tool is useful for version control and manual inspection "
        "of ODF documents, as the flat XML format is a single plain text file "
        "that can be easily viewed, edited, and compared with standard text tools. "
        "Flat ODF files typically have extensions like .fodt, .fods, .fodp, .fodg, etc."
    )
    parser = ArgumentParser(prog=PROG, description=description, epilog=epilog)
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROG} v{__version__}",
    )
    parser.add_argument(
        "file_or_folder",
        action="store",
        help="file or folder to convert",
    )
    return parser


def parse_cli_args(cli_args: list[str] | None = None) -> Namespace:
    parser = configure_parser()
    return parser.parse_args(cli_args)


def main() -> None:
    args: Namespace = parse_cli_args()
    main_convert_flat(args)


def main_convert_flat(args: Namespace) -> None:
    try:
        convert_flat(args.file_or_folder)
    except Exception as e:
        configure_parser().print_help()
        print()
        print(f"Error: {e}")
        raise SystemExit(1) from None


def is_flat_xml_file(path: Path) -> bool:
    """Check if the path is a flat ODF XML file by extension or content."""
    # Check extension first
    if path.suffix.lower() in FLAT_EXT_MAP:
        return True
    # If .xml extension or no recognized extension, check content
    if path.suffix.lower() in (".xml", ""):
        try:
            content = path.read_bytes()
            # Quick check for XML declaration and office:document element
            if content.lstrip().startswith(b"<?xml") and b"office:document" in content:
                # Just bet format is ok
                return True
        except OSError:
            pass
    return False


def convert_flat(path_str: str) -> None:
    path = Path(path_str)

    if not path.exists():
        raise ValueError(f"Path does not exist: {path}")

    # Determine if input is flat XML or needs to be converted to flat XML
    if path.is_dir():
        # Folder -> Flat XML
        out_packaging = XML
        document = Document(path)
        document.save(packaging=out_packaging, pretty=True)
    elif path.is_file():
        if is_flat_xml_file(path):
            # Flat XML -> ZIP (standard ODF)
            out_packaging = ZIP
            document = Document(path)
            # Change extension from flat to regular ODF
            # e.g., .fodt -> .odt, .fods -> .ods
            flat_ext = path.suffix.lower()
            new_ext = FLAT_EXT_MAP.get(flat_ext, ".odt")
            target_path = path.with_suffix(new_ext)
            document.save(
                target=target_path,
                packaging=out_packaging,
                pretty=True,
            )
        else:
            # ZIP or other ODF file -> Flat XML
            out_packaging = XML
            document = Document(path)
            document.save(packaging=out_packaging, pretty=True)
    else:
        raise ValueError(f"Not a file or folder: {path}")


if __name__ == "__main__":
    main()
