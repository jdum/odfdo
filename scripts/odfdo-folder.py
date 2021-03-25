#!/usr/bin/env python
# Copyright 2018 Jérôme Dumonteil
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

import os
from optparse import OptionParser
import sys

from odfdo import __version__
from odfdo import Document

if __name__ == "__main__":
    usage = "%prog <input>"
    description = "Convert standard ODF File to folder, and reverse."
    parser = OptionParser(usage, version=__version__, description=description)

    # Parse !
    options, args = parser.parse_args()

    # Go !
    if len(args) != 1:
        parser.print_help()
        sys.exit(0)

    if os.path.isfile(args[0]):
        out_packaging = "folder"
    elif os.path.isdir(args[0]):
        out_packaging = "zip"
    else:
        raise ValueError("no File or folder ?")
    doc = Document(args[0])
    doc.save(packaging=out_packaging, pretty=True)
