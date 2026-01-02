# Copyright 2018-2026 Jérôme Dumonteil
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
from odfdo.form_controls import FormText


@pytest.fixture
def form_text() -> Iterable[FormText]:
    yield FormText(
        name="some name",
        control_implementation="some implem",
        value="initial",
        current_value="final",
        convert_empty_to_null=False,
        data_field="",
        linked_cell="",
        readonly=False,
        disabled=False,
        printable=True,
        tab_index=4,
        tab_stop=False,
        max_length=12,
        xml_id="control1",
    )


def test_form_text_class():
    form = FormText()
    assert isinstance(form, FormText)


def test_form_text_minimal_tag():
    form = Element.from_tag("<form:text/>")
    assert isinstance(form, FormText)


def test_form_text_serialize():
    form = FormText()
    assert form.serialize() == "<form:text/>"


def test_form_text_repr():
    form = FormText()
    assert repr(form) == "<FormText name=None xml_id=None>"


def test_form_text_name(form_text):
    assert form_text.name == "some name"


def test_form_text_control_implementation(form_text):
    assert form_text.control_implementation == "some implem"


def test_form_text_disabled(form_text):
    assert form_text.disabled is False


def test_form_text_printable(form_text):
    assert form_text.printable is True


def test_form_text_tab_index(form_text):
    assert form_text.tab_index == 4


def test_form_text_tab_stop(form_text):
    assert form_text.tab_stop is False


def test_form_text_xml_id(form_text):
    assert form_text.xml_id == "control1"


def test_form_text_form_id(form_text):
    assert form_text.form_id == "control1"


def test_form_text_xforms_bind():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        xforms_bind="bind id",
    )
    assert form.xforms_bind == "bind id"


def test_form_text_form_id_2():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.form_id == "control1"


def test_form_text_form_value(form_text):
    assert form_text.value == "initial"


def test_form_text_form_current_value(form_text):
    assert form_text.current_value == "final"


def test_form_text_form_as_dict(form_text):
    expected = {
        "tag": "form:text",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": "final",
        "str": "final",
    }
    assert form_text.as_dict() == expected


def test_form_text_form_current_value_2(form_text):
    form_text.current_value = None
    assert form_text.current_value is None


def test_form_text_form_as_dict2(form_text):
    form_text.current_value = None
    expected = {
        "tag": "form:text",
        "name": "some name",
        "xml_id": "control1",
        "value": "initial",
        "current_value": None,
        "str": "initial",
    }
    assert form_text.as_dict() == expected


def test_form_text_convert_empty_to_null(form_text):
    assert form_text.convert_empty_to_null is False


def test_form_text_data_field(form_text):
    assert form_text.data_field == ""


def test_form_text_linked_cell(form_text):
    assert form_text.linked_cell == ""


def test_form_text_readonly(form_text):
    assert form_text.readonly is False


def test_form_text_max_length_1(form_text):
    assert form_text.max_length == 12


def test_form_text_max_length_2():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    assert form.max_length is None


def test_form_text_max_length_3():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
        max_length=15,
    )
    form.max_length = None
    assert form.max_length is None


def test_form_text_max_length_4():
    form = FormText(
        name="some name",
        value="some value",
        control_implementation="some implem",
        xml_id="control1",
        form_id="control1",
    )
    form.max_length = -4
    assert form.max_length == 0
