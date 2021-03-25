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
# Authors: David Versmisse <david.versmisse@itaapy.com>

from difflib import unified_diff, ndiff
from optparse import OptionParser
import sys
from time import ctime
from os import stat

from odfdo import __version__
from odfdo import Document

if __name__ == "__main__":
    usage = "%prog <doc1.odt> <doc2.odt>"
    description = "Show a diff between doc1.odt and doc2.odt"
    parser = OptionParser(usage, version=__version__, description=description)

    # --ndiff
    parser.add_option(
        "-n",
        "--ndiff",
        action="store_true",
        default=False,
        help='use a contextual "ndiff" format to show the output',
    )

    # Parse !
    options, args = parser.parse_args()

    # Go !
    if len(args) != 2:
        parser.print_help()
        sys.exit(1)

    # Open the 2 documents, diff only for ODT
    doc1 = Document(args[0])
    doc2 = Document(args[1])
    if doc1.get_type() != "text" or doc2.get_type() != "text":
        parser.print_help()
        sys.exit(1)

    # Convert in text before the diff
    text1 = doc1.get_formatted_text(True).splitlines(True)
    text2 = doc2.get_formatted_text(True).splitlines(True)

    # Make the diff !
    if options.ndiff:
        result = ndiff(text1, text2, None, None)
        result = [line for line in result if not line.startswith(" ")]
    else:
        fromdate = ctime(stat(args[0]).st_mtime)
        todate = ctime(stat(args[1]).st_mtime)
        result = unified_diff(text1, text2, args[0], args[1], fromdate, todate)
    print("".join(result))
