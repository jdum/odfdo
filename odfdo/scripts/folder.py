# Copyright 2018-2024 Jérôme Dumonteil
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

import sys
from optparse import OptionParser
from pathlib import Path

from odfdo import Document, __version__


def main() -> None:
    usage = "%prog <input file_or_folder>"
    description = "Convert standard ODF file to folder, and reverse."
    parser = OptionParser(usage, version=__version__, description=description)

    # Parse !
    options, args = parser.parse_args()

    try:
        convert_folder(args[0])
    except Exception as e:
        parser.print_help()
        print()
        print(repr(e))
        sys.exit(1)


def convert_folder(path_str: str) -> None:
    path = Path(path_str)
    if path.is_file():
        out_packaging = "folder"
    elif path.is_dir():
        out_packaging = "zip"
    else:
        raise ValueError(f"Not a file or folder: {path}")
    document = Document(path)
    document.save(packaging=out_packaging, pretty=True)


if __name__ == "__main__":  # pragma: no cover
    main()
