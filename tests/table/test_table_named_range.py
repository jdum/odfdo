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

from collections.abc import Iterable

import pytest

from odfdo.document import Document
from odfdo.named_range import NamedRange
from odfdo.table import Table


@pytest.fixture
def table(samples) -> Iterable[Table]:
    # simpletable :
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1	1	1	2	3	3	3
    #   1   2	3	4	5	6	7
    document = Document(samples("simple_table.ods"))
    yield document.body.get_table(name="Example1")


@pytest.fixture
def table2(samples) -> Iterable[Table]:
    document = Document(samples("simple_table_named_range.ods"))
    yield document.body.get_table(name="Example1")


def test_create_bad_nr():
    with pytest.raises(ValueError):
        NamedRange()


def test_create_bad_nr_2():
    with pytest.raises(ValueError):
        NamedRange(" ", "A1", "tname")


def test_create_bad_nr_3():
    with pytest.raises(ValueError):
        NamedRange("A1", "A1", "tname")


def test_create_bad_nr_4():
    with pytest.raises(ValueError):
        NamedRange("a space", "A1", "tname")


def test_create_bad_nr_5():
    with pytest.raises(ValueError):
        NamedRange("===", "A1", "tname")


def test_create_bad_nr_6():
    with pytest.raises(ValueError):
        NamedRange("ok", "A1", "/ ")


def test_create_bad_nr_7():
    with pytest.raises(ValueError):
        NamedRange("ok", "A1", " ")


def test_create_bad_nr_8():
    with pytest.raises(ValueError):
        NamedRange("ok", "A1", "\\")


def test_create_bad_nr_9():
    with pytest.raises(ValueError):
        NamedRange("ok", "A1", "tname\nsecond line")


def test_create_bad_nr_10():
    with pytest.raises(TypeError):
        NamedRange("ok", "A1", 42)


def test_create_nr():
    nr = NamedRange("nr_name_ù", "A1:C2", "table name é", usage="filter")
    result = (
        """<table:named-range table:name="nr_name_ù" """
        """table:base-cell-address="$'table name é'.$A$1" """
        """table:cell-range-address="$'table name é'.$A$1:.$C$2" """
        """table:range-usable-as="filter"/>"""
    )
    assert nr.serialize() == result


def test_usage_1():
    nr = NamedRange("a123a", "A1:C2", "tablename")
    assert nr.usage is None
    nr.set_usage("blob")
    assert nr.usage is None


def test_usage_2():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.set_usage("filter")
    assert nr.usage == "filter"
    nr.set_usage("blob")
    assert nr.usage is None


def test_usage_3():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.set_usage("Print-Range")
    assert nr.usage == "print-range"
    nr.set_usage(None)
    assert nr.usage is None


def test_usage_4():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.set_usage("repeat-column")
    assert nr.usage == "repeat-column"


def test_usage_5():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.set_usage("repeat-row")
    assert nr.usage == "repeat-row"


def test_name_1():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    assert nr.name == "nr_name"


def test_name_2():
    NAME = "New_Name_ô"
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.name = f"  {NAME} "
    assert nr.name == NAME


def test_name_3():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    try:
        nr.name = "   "
        ok = True
    except Exception:
        ok = False
    assert ok is False


def test_table_name_1():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    assert nr.table_name == "tablename"


def test_table_name_2():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.set_table_name("  new name ")
    assert nr.table_name == "new name"


def test_table_name_3():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    with pytest.raises(ValueError):
        nr.set_table_name("   ")


def test_range_1():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    with pytest.raises(TypeError):
        nr.set_range("   ")


def test_range_2():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    assert nr.crange == (0, 0, 2, 1)
    assert nr.start == (0, 0)
    assert nr.end == (2, 1)


def test_range_3():
    nr = NamedRange("nr_name", "A1", "tablename")
    assert nr.crange == (0, 0, 0, 0)
    assert nr.start == (0, 0)
    assert nr.end == (0, 0)


def test_range_4():
    nr = NamedRange("nr_name", (1, 2, 3, 4), "tablename")
    assert nr.crange == (1, 2, 3, 4)
    assert nr.start == (1, 2)
    assert nr.end == (3, 4)


def test_range_5():
    nr = NamedRange("nr_name", (5, 6), "tablename")
    assert nr.crange == (5, 6, 5, 6)
    assert nr.start == (5, 6)
    assert nr.end == (5, 6)


def test_range_6():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.set_range("B3")
    assert nr.crange == (1, 2, 1, 2)
    assert nr.start == (1, 2)
    assert nr.end == (1, 2)


def test_range_7():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.set_range("B3:b10")
    assert nr.crange == (1, 2, 1, 9)
    assert nr.start == (1, 2)
    assert nr.end == (1, 9)


def test_range_8():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.set_range((1, 5, 0, 9))
    assert nr.crange == (1, 5, 0, 9)
    assert nr.start == (1, 5)
    assert nr.end == (0, 9)


def test_range_9():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    nr.set_range((0, 9))
    assert nr.crange == (0, 9, 0, 9)
    assert nr.start == (0, 9)
    assert nr.end == (0, 9)


def test_value_bad_1():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    with pytest.raises(ValueError):
        nr.get_values()


def test_value_bad_2():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    with pytest.raises(ValueError):
        nr.get_value()


def test_value_bad_3():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    with pytest.raises(ValueError):
        nr.set_values([[1, 2]])


def test_value_bad_4():
    nr = NamedRange("nr_name", "A1:C2", "tablename")
    with pytest.raises(ValueError):
        nr.set_value(42)


def test_body_table_get_1(table):
    assert table.get_named_ranges() == []


def test_body_table_get_2(table2):
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["nr_1", "nr_6"]


def test_body_table_get_3(table2):
    assert len(table2.get_named_ranges()) == 2


def test_body_table_get_4(table2):
    back_nr = table2.get_named_range("nr_1")
    n = back_nr.name
    assert n == "nr_1"


def test_body_table_get_4_1(table2):
    back_nr = table2.get_named_range("nr_1xxx")
    assert back_nr is None


def test_body_table_get_4_2(table2):
    back_nr = table2.get_named_range("nr_6")
    assert back_nr.name == "nr_6"
    assert back_nr.table_name == "Example1"
    assert back_nr.start == (3, 2)
    assert back_nr.end == (5, 3)
    assert back_nr.crange == (3, 2, 5, 3)
    assert back_nr.usage == "print-range"


def test_body_table_get_5(table):
    back_nr = table.get_named_range("nr_1")
    assert back_nr is None


def test_body_table_set_0(table2):
    with pytest.raises(ValueError):
        table2.set_named_range("   ", "A1:C2")


def test_body_table_set_1(table2):
    table2.set_named_range("new", "A1:B1")
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["nr_1", "nr_6", "new"]


def test_body_table_set_3(table2):
    table2.set_named_range("new", "A1:B1")
    back_nr = table2.get_named_range("new")
    assert back_nr.usage is None
    assert back_nr.crange == (0, 0, 1, 0)
    assert back_nr.start == (0, 0)
    assert back_nr.end == (1, 0)
    assert back_nr.table_name == "Example1"
    # reset
    table2.set_named_range("new", "A1:c2")
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["nr_1", "nr_6", "new"]
    back_nr = table2.get_named_range("new")
    assert back_nr.usage is None
    assert back_nr.crange == (0, 0, 2, 1)
    assert back_nr.start == (0, 0)
    assert back_nr.end == (2, 1)
    assert back_nr.table_name == "Example1"


def test_body_table_delete_1(table2):
    table2.delete_named_range("xxx")
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["nr_1", "nr_6"]


def test_body_table_delete_2(table2):
    table2.delete_named_range("nr_1")
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["nr_6"]


def test_body_table_delete_3(table2):
    table2.set_named_range("new", "A1:c2")
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["nr_1", "nr_6", "new"]
    table2.delete_named_range("nr_1")
    table2.delete_named_range("nr_6")
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["new"]
    table2.delete_named_range("new")
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == []
    table2.delete_named_range("new")
    table2.delete_named_range("xxx")
    table2.set_named_range("hop", "A1:C2")
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["hop"]
    table2.set_named_range("hop", "A2:d8")
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["hop"]
    nr = table2.get_named_range("hop")
    assert nr.crange == (0, 1, 3, 7)


def test_body_table_get_value_1(table2):
    result = table2.get_named_range("nr_1").get_value()
    assert result == 1


def test_body_table_get_value_2(table2):
    result = table2.get_named_range("nr_1").get_value(get_type=True)
    assert result == (1, "float")


def test_body_table_get_value_3(table2):
    result = table2.get_named_range("nr_1").get_values()
    assert result == [[1]]


def test_body_table_get_value_4(table2):
    result = table2.get_named_range("nr_1").get_values(flat=True)
    assert result == [1]


def test_body_table_get_value_5(table2):
    result = table2.get_named_range("nr_6").get_values(flat=True)
    assert result == [2, 3, 3, 4, 5, 6]


def test_body_table_get_value_6(table2):
    result = table2.get_named_range("nr_6").get_value()
    assert result == 2


def test_body_table_set_value_1(table2):
    table2.get_named_range("nr_6").set_value("AAA")
    assert table2.get_value("D3") == "AAA"
    assert table2.get_value("E3") == 3


def test_body_table_set_value_2(table2):
    table2.get_named_range("nr_6").set_values([[10, 11, 12], [13, 14, 15]])
    assert table2.get_values() == [
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 2, 3, 3, 3],
        [1, 1, 1, 10, 11, 12, 3],
        [1, 2, 3, 13, 14, 15, 7],
    ]


def test_body_change_name_table(table2):
    table2.name = "new table"
    result = [nr.name for nr in table2.get_named_ranges()]
    assert result == ["nr_1", "nr_6"]
    back_nr = table2.get_named_range("nr_6")
    assert back_nr.name == "nr_6"
    assert back_nr.table_name == "new table"
    assert back_nr.start == (3, 2)
    assert back_nr.end == (5, 3)
    assert back_nr.crange == (3, 2, 5, 3)
    assert back_nr.usage == "print-range"
