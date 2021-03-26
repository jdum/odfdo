# Copyright 2018-2020 Jérôme Dumonteil
# Copyright (c) 2010 Ars Aperta, Itaapy, Pierlis, Talend.
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
"""Utilities shared by the scripts
"""
import sys
from sys import stdin, stdout, stderr
from mimetypes import guess_type
from os.path import exists, isfile
from io import StringIO


def check_target_file(path, kind="file"):
    if exists(path):
        message = 'The %s "%s" exists, overwrite it? [y/N]'
        stderr.write(message % (kind, path))
        stderr.flush()
        line = stdin.readline()
        line = line.strip().lower()
        if line != "y":
            stderr.write("Operation aborted\n")
            stderr.flush()
            sys.exit(0)


def check_target_directory(path):
    return check_target_file(path, kind="directory")


encoding_map = {"gzip": "application/x-gzip", "bzip2": "application/x-bzip2"}


def get_mimetype(filename):
    if not isfile(filename):
        return "application/x-directory"
    mimetype, encoding = guess_type(filename)
    if encoding is not None:
        return encoding_map.get(encoding, encoding)
    if mimetype is not None:
        return mimetype
    return "application/octet-stream"


def add_option_output(parser, metavar="FILE", complement=""):
    msg = f"dump the output into {metavar} {complement}"
    parser.add_option("-o", "--output", metavar=metavar, help=msg)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def printinfo(*args, **kw):
    indent = kw.get("indent", 0)
    if indent:
        stderr.write(" " * indent)
    output = " ".join(str(arg) for arg in args)
    eprint(output)


def printwarn(*args, **kw):
    printinfo("Warning:", *args, **kw)


def printerr(*args, **kw):
    printinfo("Error:", *args, **kw)


# FIXME: still broken ?
class StdoutWriter(StringIO):
    """Some proxy to write output to stdout in scripts. Because The zipfile
    module raises "IOError: [Errno 29] Illegal seek" when writing to stdout
    directly.
    """

    def write(self, s):
        stdout.write(s)
        StringIO.write(self, s)
