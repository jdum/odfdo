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
#          Jerome Dumonteil <jerome.dumonteil@itaapy.com>

from collections.abc import Iterable
from datetime import datetime

import pytest

from odfdo.document import Document
from odfdo.user_field import UserDefined


@pytest.fixture
def document(samples) -> Iterable[Document]:
    document = Document(samples("meta.odt"))
    yield document


def test_user_defined_class():
    field = UserDefined()
    assert isinstance(field, UserDefined)


def test_user_defined_style():
    field = UserDefined(style="some_style")
    assert field.style == "some_style"


def test_create_user_defined_1(document):
    element = UserDefined(
        "unknown_in_meta",
        value=42,
        value_type="float",
        text=None,
        style=None,
        from_document=document,
    )
    expected = (
        '<text:user-defined text:name="unknown_in_meta" '
        'office:value-type="float" calcext:value-type="float" '
        'office:value="42" calcext:value="42">42'
        "</text:user-defined>"
    )
    assert element.serialize() == expected


def test_create_user_defined_2(document):
    element = UserDefined(
        "unknown_in_meta2",
        value=datetime(2013, 12, 30),
        value_type="date",
        text="2013-12-30",
        style=None,
        from_document=document,
    )
    expected = (
        '<text:user-defined text:name="unknown_in_meta2" '
        'office:value-type="date" calcext:value-type="date" '
        'office:date-value="2013-12-30T00:00:00">2013-12-30'
        "</text:user-defined>"
    )
    assert element.serialize() == expected


def test_create_user_defined_2_no_doc():
    element = UserDefined(
        "unknown_in_meta2",
        value=datetime(2013, 12, 30),
        value_type="date",
        text="2013-12-30",
        style=None,
        from_document=None,
    )
    expected = (
        '<text:user-defined text:name="unknown_in_meta2" '
        'office:value-type="date" calcext:value-type="date" '
        'office:date-value="2013-12-30T00:00:00">2013-12-30'
        "</text:user-defined>"
    )
    assert element.serialize() == expected


def test_create_user_defined_3_existing(document):
    element = UserDefined("Référence", from_document=document)
    expected = (  # noqa: UP031
        '<text:user-defined text:name="%s" '
        'office:value-type="boolean" calcext:value-type="boolean" '
        'office:boolean-value="true">true</text:user-defined>'
    ) % "Référence"
    assert element.serialize() == expected


def test_create_user_defined_4_existing(document):
    element = UserDefined(
        "Référence",
        value=False,  # default value if not existing
        value_type="boolean",
        from_document=document,
    )
    expected = (  # noqa: UP031
        '<text:user-defined text:name="%s" '
        'office:value-type="boolean" calcext:value-type="boolean" '
        'office:boolean-value="true">true</text:user-defined>'
    ) % "Référence"
    assert element.serialize() == expected


def test_create_user_defined_5_nodoc():
    element = UserDefined(
        "Référence",
        value=False,  # default value if not existing
        value_type="boolean",
        from_document=None,
    )
    expected = (  # noqa: UP031
        '<text:user-defined text:name="%s" '
        'office:value-type="boolean" calcext:value-type="boolean" '
        'office:boolean-value="false">false</text:user-defined>'
    ) % "Référence"
    assert element.serialize() == expected


def test_get_user_defined(document):
    element = UserDefined(
        "Référence",
        value=False,  # default value if not existing
        value_type="boolean",
        from_document=document,
    )
    body = document.body
    para = body.get_paragraph()
    para.append(element)
    user_defined = body.get_user_defined("Référence")
    expected = (  # noqa: UP031
        '<text:user-defined text:name="%s" '
        'office:value-type="boolean" calcext:value-type="boolean" '
        'office:boolean-value="true">true</text:user-defined>'
    ) % "Référence"
    assert user_defined.serialize() == expected


def test_get_user_defined_list(document):
    element = UserDefined(
        "Référence",
        value=False,  # default value if not existing
        value_type="boolean",
        from_document=document,
    )
    body = document.body
    para = body.get_paragraph()
    para.append(element)
    element2 = UserDefined(
        "unknown_in_meta2",
        value=datetime(2013, 12, 30),
        value_type="date",
        text="2013-12-30",
        style=None,
        from_document=None,
    )
    para.append(element2)
    user_defined_list = body.get_user_defined_list()
    assert len(user_defined_list) == 2


def test_get_user_defined_list_property(document):
    element = UserDefined(
        "Référence",
        value=False,  # default value if not existing
        value_type="boolean",
        from_document=document,
    )
    body = document.body
    para = body.get_paragraph()
    para.append(element)
    element2 = UserDefined(
        "unknown_in_meta2",
        value=datetime(2013, 12, 30),
        value_type="date",
        text="2013-12-30",
        style=None,
        from_document=None,
    )
    para.append(element2)
    user_defined_list = body.user_defined_list
    assert len(user_defined_list) == 2


def test_get_user_defined_value(document):
    element = UserDefined(
        "Référence",
        value=True,  # default value if not existing
        value_type="boolean",
        from_document=document,
    )
    body = document.body
    para = body.get_paragraph()
    para.append(element)
    element2 = UserDefined(
        "unknown_in_meta2",
        value=datetime(2013, 12, 30),
        value_type="date",
        text="2013-12-30",
        style=None,
        from_document=None,
    )
    para.append(element2)
    value = body.get_user_defined_value("Référence")
    assert value is True
    value = body.get_user_defined_value("unknown_in_meta2")
    assert value == datetime(2013, 12, 30)
