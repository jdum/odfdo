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

from __future__ import annotations

from collections.abc import Iterable

import pytest

from odfdo import Element
from odfdo.form_controls import FormHidden


@pytest.fixture
def form_hidden() -> Iterable[FormHidden]:
    yield FormHidden(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
    )


def test_form_hidden_class():
    form = FormHidden()
    assert isinstance(form, FormHidden)


def test_form_hidden_minimal_tag():
    form = Element.from_tag("<form:hidden/>")
    assert isinstance(form, FormHidden)


def test_form_hidden_serialize():
    form = FormHidden()
    assert form.serialize() == "<form:hidden/>"


def test_form_hidden_repr():
    form = FormHidden()
    assert repr(form) == "<FormHidden name=None xml_id=None>"


def test_form_hidden_name(form_hidden):
    assert form_hidden.name == "some name"


def test_form_hidden_str(form_hidden):
    assert str(form_hidden) == ""


def test_form_hidden_as_dict(form_hidden):
    expected = {
        "tag": "form:hidden",
        "name": "some name",
        "xml_id": "control1",
        "value": "some value",
        "current_value": None,
        "str": "",
    }
    assert form_hidden.as_dict() == expected


def test_form_hidden_control_implementation(form_hidden):
    assert form_hidden.control_implementation == "some implem"


def test_form_hidden_xml_id(form_hidden):
    assert form_hidden.xml_id == "control1"


def test_form_hidden_form_id(form_hidden):
    assert form_hidden.form_id == "control1"


def test_form_hidden_xforms_bind():
    form = FormHidden(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_hidden_form_id_2():
    form = FormHidden(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"
