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

import pytest

from odfdo.table import Table


def test_default():
    table = Table("A Table")
    expected = '<table:table table:name="A Table"/>'
    assert table.serialize() == expected


def test_bad_name_empty():
    pytest.raises(TypeError, Table)


def test_bad_name_1():
    pytest.raises(ValueError, Table, " ")


def test_good_apos():
    _t = Table("ee'ee")


def test_bad_name_2():
    pytest.raises(ValueError, Table, "'eeee")


def test_bad_name_2_right():
    pytest.raises(ValueError, Table, "eeee'")


def test_bad_name_3():
    pytest.raises(ValueError, Table, "ee/ee")


def test_bad_name_4():
    pytest.raises(ValueError, Table, "ee\nee")


def test_bad_name_5():
    pytest.raises(ValueError, Table, "ee\\ee")


def test_bad_name_6():
    pytest.raises(ValueError, Table, "ee*ee")


def test_bad_name_7():
    pytest.raises(ValueError, Table, "ee?ee")


def test_bad_name_8():
    pytest.raises(ValueError, Table, "ee:ee")


def test_bad_name_9():
    pytest.raises(ValueError, Table, "ee]ee")


def test_bad_name_10():
    pytest.raises(ValueError, Table, "ee[ee")


def test_width_height():
    table = Table("A Table", width=1, height=2)
    expected = (
        '<table:table table:name="A Table">'
        "<table:table-column/>"
        "<table:table-row>"
        "<table:table-cell/>"
        "</table:table-row>"
        "<table:table-row>"
        "<table:table-cell/>"
        "</table:table-row>"
        "</table:table>"
    )
    assert table.serialize() == expected


def test_width_height_str():
    table = Table("A Table", width="1", height="2")
    expected = (
        '<table:table table:name="A Table">'
        "<table:table-column/>"
        "<table:table-row>"
        "<table:table-cell/>"
        "</table:table-row>"
        "<table:table-row>"
        "<table:table-cell/>"
        "</table:table-row>"
        "</table:table>"
    )
    assert table.serialize() == expected


def test_print():
    table = Table("Printable")
    expected = '<table:table table:name="Printable"/>'
    assert table.serialize() == expected


def test_print_false():
    table = Table("Hidden", printable=False)
    expected = '<table:table table:name="Hidden" table:print="false"/>'
    assert table.serialize() == expected


def test_print_ranges_str():
    table = Table("Ranges", print_ranges="E6:K12 P6:R12")
    expected = '<table:table table:name="Ranges" table:print-ranges="E6:K12 P6:R12"/>'
    assert table.serialize() == expected


def test_print_ranges_list():
    table = Table("Ranges", print_ranges=["E6:K12", "P6:R12"])
    expected = '<table:table table:name="Ranges" table:print-ranges="E6:K12 P6:R12"/>'
    assert table.serialize() == expected


def test_style():
    table = Table("A Table", style="A Style")
    expected = '<table:table table:name="A Table" table:style-name="A Style"/>'
    assert table.serialize() == expected
