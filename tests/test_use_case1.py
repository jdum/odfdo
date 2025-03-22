# Copyright 2018-2025 Jérôme Dumonteil
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
from mimetypes import guess_type

from PIL import Image

from odfdo import (
    FIRST_CHILD,
    Cell,
    Column,
    Document,
    Frame,
    Header,
    Paragraph,
    Row,
    Table,
    __version__,
)


def use_case1(destination_file, smp_dir):
    print("odfdo test use case 1")
    print(f"version: {__version__}")
    print(f"Generating test file {destination_file}")

    document = Document("text")
    body = document.body

    for numero, path in enumerate(smp_dir.iterdir()):
        # print(numero, path)
        filename = path.name
        heading = Header(1, text=filename)
        body.append(heading)
        mimetype, _ = guess_type(filename)
        if not mimetype:
            mimetype = "application/octet-stream"
        if mimetype.startswith("image/"):
            # Add the image
            print(path)
            image_uri = document.add_file(path)
            print("->", image_uri)
            # compute size
            image = Image.open(path)
            width, height = image.size
            draw_size = (f"{width / 400:.2f}in", f"{height / 400:.2f}in")
            image_frame = Frame.image_frame(
                image_uri,
                size=draw_size,
                anchor_type="char",
            )
            paragraph = Paragraph("")
            paragraph.append(image_frame)
            body.append(paragraph)
            body.append(Paragraph(""))
        elif mimetype in ("text/csv", "text/comma-separated-values"):
            print(mimetype)
            table = Table(f"table {numero}", style="Standard")
            size = 0
            with open(path) as file:
                csv = reader(file)
                for line in csv:
                    size = max(size, len(line))
                    row = Row()
                    for value in line:
                        cell = Cell(value)
                        row.append_cell(cell)
                    table.append_row(row)
                for _i in range(size):
                    column = Column(style="Standard")
                    table.insert(column, FIRST_CHILD)
            body.append(table)
        else:
            paragraph = Paragraph("Not image or csv", style="Standard")
            body.append(paragraph)

    destination_file.parent.mkdir(parents=True, exist_ok=True)
    document.save(destination_file, pretty=True)


def test_use_case1(tmp_path, samples_dir):
    path = tmp_path / "use_case_1.odt"
    use_case1(path, samples_dir)
    assert path.is_file()
