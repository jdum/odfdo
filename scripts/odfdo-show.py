#!/usr/bin/env python
# Copyright 2018 Jérôme Dumonteil
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

from optparse import OptionParser
from os import mkdir, makedirs
from os.path import join, exists
from shutil import rmtree
from sys import exit, stdout

from odfdo import __version__
# from odfdo.cleaner import test_document
from odfdo import Document
from odfdo.scriptutils import add_option_output, printerr
from odfdo.scriptutils import check_target_directory


def clean_filename(filename):
    allowed_characters = {'.', '-', '_', '@'}
    result = []
    for c in filename:
        if c not in allowed_characters and not c.isalnum():
            result.append('_')
        else:
            result.append(c)
    return ''.join(result)


def dump_pictures(document, target):
    for part_name in document.get_parts():
        if part_name.startswith('Pictures/'):
            path = join(target, "Pictures")
            if not exists(path):
                mkdir(path)
            data = document.get_part(part_name)
            path = join(target, part_name)
            with open(path, 'wb') as f:
                f.write(data)


def spreadsheet_to_stdout(document):
    body = document.body
    for table in body.get_tables():
        table.rstrip(aggressive=True)
        print(table.to_csv(None))


def spreadsheet_to_csv(document, target):
    body = document.get_body()
    for table in body.get_tables():
        name = table.get_name()
        filename = clean_filename(name) + '.csv'
        table.rstrip(aggressive=True)
        table.to_csv(filename)


if __name__ == '__main__':
    # Options initialisation
    usage = ('%prog [--styles] [--meta] [--no-content] [--rst] <file>\n'
             '       %prog -o <DIR> [--rst] <file>')
    description = ("Dump text from an OpenDocument file to the standard "
                   "output, optionally styles and meta (and the Pictures/* in "
                   '"-o <DIR>" mode)')
    parser = OptionParser(usage, version=__version__, description=description)
    # --meta
    parser.add_option(
        '-m',
        '--meta',
        action='store_true',
        default=False,
        help='dump metadata to stdout')
    # --styles
    parser.add_option(
        '-s',
        '--styles',
        action='store_true',
        default=False,
        help='dump styles to stdout')
    # --no-content
    parser.add_option(
        '-n',
        '--no-content',
        action='store_true',
        default=False,
        help='do not dump content to stdout')
    # --rst
    parser.add_option(
        '-r',
        '--rst',
        action='store_true',
        default=False,
        help='Dump the content file with a reST syntax')
    # --output
    add_option_output(parser, metavar="DIR")
    # Parse !
    options, args = parser.parse_args()
    # Container
    if len(args) != 1:
        parser.print_help()
        exit(1)
    container_url = args[0]
    # Open it!
    document = Document(container_url)
    doc_type = document.get_type()
    # Test it! XXX for TEXT only
    #if doc_type == 'text':
    #    result = test_document(document)
    #    if result is not True:
    #        print('This file is malformed: %s' % result)
    #        print('Please use lpod-clean.py to fix it')
    #        exit(1)
    if options.output:
        target = options.output
        check_target_directory(target)
        if exists(target):
            rmtree(target)
        makedirs(target)
        with open(join(target, 'meta.txt'), 'w') as f:
            f.write(document.get_formated_meta())
        with open(join(target, 'styles.txt'), 'w') as f:
            f.write(document.show_styles())
        dump_pictures(document, target)
    else:
        if options.meta:
            print(document.get_formated_meta())
        if options.styles:
            print(document.show_styles())
    # text
    if doc_type in ('text', 'text-template', 'presentation',
                    'presentation-template'):
        if options.output:
            with open(join(target, 'content.rst'), 'w') as f:
                f.write(document.get_formatted_text(rst_mode=options.rst))
        elif not options.no_content:
            print(document.get_formatted_text(rst_mode=options.rst))
    # spreadsheet
    elif doc_type in ('spreadsheet', 'spreadsheet-template'):
        if options.output:
            spreadsheet_to_csv(document, target)
        elif not options.no_content:
            spreadsheet_to_stdout(document)
    else:
        printerr("The OpenDocument format", doc_type, "is not supported yet.")
        exit(1)
