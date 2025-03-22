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
from io import StringIO

import pytest

from odfdo.table import Table, import_from_csv

CSV_DATA = '"A float","3.14"\n"A date","1975-05-07"\n'


@pytest.fixture
def table() -> Iterable[Table]:
    table = import_from_csv(StringIO(CSV_DATA), "From CSV")
    yield table


def test_import_from_csv(table):
    expected = (
        '<table:table table:name="From CSV">'
        "<table:table-column "
        'table:number-columns-repeated="2"/>'
        "<table:table-row>"
        '<table:table-cell office:value-type="string" '
        'calcext:value-type="string" '
        'office:string-value="A float">'
        "<text:p>A float</text:p>"
        "</table:table-cell>"
        '<table:table-cell office:value-type="float" '
        'calcext:value-type="float" '
        'office:value="3.14" calcext:value="3.14">'
        "<text:p>3.14</text:p>"
        "</table:table-cell>"
        "</table:table-row>"
        "<table:table-row>"
        '<table:table-cell office:value-type="string" '
        'calcext:value-type="string" '
        'office:string-value="A date">'
        "<text:p>A date</text:p>"
        "</table:table-cell>"
        '<table:table-cell office:value-type="date" '
        'calcext:value-type="date" '
        'office:date-value="1975-05-07T00:00:00">'
        "<text:p>1975-05-07T00:00:00</text:p>"
        "</table:table-cell>"
        "</table:table-row>"
        "</table:table>"
    )
    assert table.serialize() == expected


def test_export_to_csv(table):
    expected = "A float,3.14\r\nA date,1975-05-07 00:00:00\r\n"
    assert table.to_csv() == expected
