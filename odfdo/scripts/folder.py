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
# Authors: Jerome Dumonteil <jerome.dumonteil@itaapy.com>
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from odfdo import Document, __version__
from odfdo.const import FOLDER, ZIP

PROG = "odfdo-folder"


def configure_parser() -> ArgumentParser:
    description = "Convert standard ODF file to folder, and reverse."
    parser = ArgumentParser(prog=PROG, description=description)
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


def main() -> None:
    parser = configure_parser()
    args = parser.parse_args()

    try:
        convert_folder(args.file_or_folder)
    except Exception as e:
        parser.print_help()
        print()
        print(f"Error: {e}")
        raise SystemExit(1) from None


def convert_folder(path_str: str) -> None:
    path = Path(path_str)
    if path.is_file():
        out_packaging = FOLDER
    elif path.is_dir():
        out_packaging = ZIP
    else:
        raise ValueError(f"Not a file or folder: {path}")
    document = Document(path)
    document.save(packaging=out_packaging, pretty=True)


if __name__ == "__main__":  # pragma: no cover
    main()
