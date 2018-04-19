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

from csv import reader
from os import listdir, mkdir
from os.path import join, exists
from mimetypes import guess_type

from PIL import Image

from odfdo import __version__
from odfdo import Document, Frame, Header, DrawImage, Paragraph, Cell, Row
from odfdo import Table, Column, FIRST_CHILD

# Hello messages
print('odfdo installation test')
print(' Version           : %s' % __version__)
print()
print('Generating test_output/use_case1.odt ...')

# Go
document = Document('text')
body = document.body

for numero, filename in enumerate(listdir('samples')):
    # Heading
    heading = Header(1, text=filename)
    body.append(heading)
    path = join('samples', filename)
    mimetype, _ = guess_type(path)
    if mimetype is None:
        mimetype = 'application/octet-stream'
    if mimetype.startswith('image/'):
        # Add the image
        internal_name = 'Pictures/' + filename
        image = Image.open(path)
        width, height = image.size
        paragraph = Paragraph('Standard')
        # 72 ppp
        frame = Frame('frame_%d' % numero, 'Graphics',
                      str(int(width / 72.0)) + 'in',
                      str(int(height / 72.0)) + 'in')
        image = DrawImage(internal_name)
        frame.append(image)
        paragraph.append(frame)
        body.append(paragraph)

        # And store the data
        container = document.container
        with open(path, 'rb') as f:
            content = f.read()
        container.set_part(internal_name, content)
    elif mimetype in ('text/csv', 'text/comma-separated-values'):
        table = Table("table %d" % numero, style="Standard")
        csv = reader(open(path))
        for line in csv:
            size = len(line)
            row = Row()
            for value in line:
                cell = Cell(value)
                row.append_cell(cell)
            table.append_row(row)
        for i in range(size):
            column = Column(style="Standard")
            table.insert(column, FIRST_CHILD)
        body.append(table)
    else:
        paragraph = Paragraph("Not image / csv", style="Standard")
        body.append(paragraph)

if not exists('test_output'):
    mkdir('test_output')
document.save('test_output/use_case1.odt', pretty=True)
