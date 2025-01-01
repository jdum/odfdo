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


from odfdo.element import Element
from odfdo.header_rows import HeaderRows


def test_create_header_rows():
    header_rows = HeaderRows()
    assert isinstance(header_rows, HeaderRows)


def test_header_rows_tag():
    header_rows = HeaderRows()
    assert header_rows._tag == "table:table-header-rows"


def test_header_rows_tag2():
    header_rows = HeaderRows()
    print(header_rows.serialize(pretty=True))
    assert header_rows.tag == "table:table-header-rows"


def test_header_rows_from():
    content = "<table:table-header-rows/>"
    element = Element.from_tag(content)
    assert element.tag == "table:table-header-rows"


def test_header_rows_from2():
    content = "<table:table-header-rows/>"
    element = Element.from_tag(content)
    assert element._tag == "table:table-header-rows"
