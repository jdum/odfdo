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
# Authors: Jerome Dumonteil <jerome.dumonteil@itaapy.com>


from odfdo import (
    Cell,
    Document,
    Row,
    Style,
    Table,
    __version__,
    create_table_cell_style,
    make_table_cell_border_string,
    rgb2hex,
)


def use_case3(destination_file):
    print("odfdo test use case 3")
    print(f"version: {__version__}")
    print(f"Generating test file {destination_file}")

    document = Document("spreadsheet")
    body = document.body
    body.clear()
    table = Table("use_case3")

    for y in range(0, 256, 8):
        row = Row()
        for x in range(0, 256, 32):
            cell_value = (x, y, (x + y) % 256)
            border_rl = make_table_cell_border_string(thick="0.20cm", color="white")
            border_bt = make_table_cell_border_string(
                thick="0.80cm",
                color="white",
            )
            style = create_table_cell_style(
                color="grey",
                background_color=cell_value,
                border_right=border_rl,
                border_left=border_rl,
                border_bottom=border_bt,
                border_top=border_bt,
            )
            name = document.insert_style(style=style, automatic=True)
            cell = Cell(value=rgb2hex(cell_value), style=name)
            row.append_cell(cell)
        table.append_row(row)

        row_style = Style("table-row", height="1.80cm")
        name_style_row = document.insert_style(style=row_style, automatic=True)
        for row in table.get_rows():
            row.style = name_style_row
            table.set_row(row.y, row)

        col_style = Style("table-column", width="3.6cm")
        name = document.insert_style(style=col_style, automatic=True)
        for column in table.columns:
            column.style = col_style
            table.set_column(column.x, column)

    body.append(table)

    destination_file.parent.mkdir(parents=True, exist_ok=True)
    document.save(destination_file, pretty=True)


def test_use_case3(tmp_path):
    path = tmp_path / "use_case_3.odt"
    use_case3(path)
    assert path.is_file()
