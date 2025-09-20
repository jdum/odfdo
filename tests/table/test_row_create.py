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

from odfdo.table import Row


def test_default():
    row = Row()
    expected = "<table:table-row/>"
    assert row.serialize() == expected


def test_width():
    row = Row(1)
    expected = "<table:table-row><table:table-cell/></table:table-row>"
    assert row.serialize() == expected


def test_repeated():
    row = Row(repeated=3)
    expected = '<table:table-row table:number-rows-repeated="3"/>'
    assert row.serialize() == expected


def test_style():
    row = Row(style="ro1")
    expected = '<table:table-row table:style-name="ro1"/>'
    assert row.serialize() == expected


def test_all():
    row = Row(1, repeated=3, style="ro1")
    expected = (
        '<table:table-row table:number-rows-repeated="3" '
        'table:style-name="ro1">'
        "<table:table-cell/>"
        "</table:table-row>"
    )
    assert row.serialize() == expected
