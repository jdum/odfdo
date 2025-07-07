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
# Authors: Romain Gauthier <romain@itaapy.com>
#          Hervé Cauwelier <herve@itaapy.com>
#          David Versmisse <david.versmisse@itaapy.com>
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from odfdo.column import Column


def test_default():
    column = Column()
    expected = "<table:table-column/>"
    assert column.serialize() == expected


def test_default_cell_style():
    column = Column(default_cell_style="A Style")
    expected = '<table:table-column table:default-cell-style-name="A Style"/>'
    assert column.serialize() == expected


def test_style():
    column = Column(style="A Style")
    expected = '<table:table-column table:style-name="A Style"/>'
    assert column.serialize() == expected


def test_all():
    column = Column(style="co1", default_cell_style="Standard", repeated=3)
    expected = (
        "<table:table-column "
        'table:default-cell-style-name="Standard" '
        'table:number-columns-repeated="3" '
        'table:style-name="co1"/>'
    )
    assert column.serialize() == expected
